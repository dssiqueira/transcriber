import sys
import os
import json
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime
from pathlib import Path
import qtawesome as qta
from PySide6.QtCore import Qt, Slot, QTimer, QSize
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTabWidget,
    QProgressBar, QFileDialog, QMessageBox,
    QRadioButton, QButtonGroup, QTableWidget, QTextEdit,
    QFrame, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QPainter, QColor, QPen

class VUMeter(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(30)
        self.setMinimumHeight(100)
        
        # Valores do medidor
        self.value = 0
        self.peak = 0
        self.decay = 0.01
        self.peak_decay = 0.005
        self.peak_hold_time = 0
        
        # Configuração visual
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setLineWidth(2)
        
    def set_value(self, value):
        """Atualiza o valor do VU meter"""
        self.value = max(0, min(1, value))
        
        # Atualiza o valor de pico
        if self.value > self.peak:
            self.peak = self.value
            self.peak_hold_time = 30
        else:
            if self.peak_hold_time > 0:
                self.peak_hold_time -= 1
            else:
                self.peak = max(0, self.peak - self.peak_decay)
        
        self.update()
    
    def paintEvent(self, event):
        """Desenha o VU meter"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenha o fundo
        rect = self.rect()
        painter.fillRect(rect, QColor("#181818"))
        
        # Calcula as dimensões
        width = rect.width()
        height = rect.height()
        bar_width = width - 4
        
        # Desenha a barra principal
        value_height = int(height * (1 - self.value))
        gradient_rect = rect.adjusted(2, value_height, -2, 0)
        
        # Cores para diferentes níveis
        if self.value < 0.6:
            color = QColor("#00d1b2")  # Verde
        elif self.value < 0.8:
            color = QColor("#ffdd57")  # Amarelo
        else:
            color = QColor("#ff3860")  # Vermelho
        
        painter.fillRect(gradient_rect, color)
        
        # Desenha a linha de pico
        peak_y = int(height * (1 - self.peak))
        peak_color = QColor("#ff3860") if self.peak > 0.8 else QColor("#ffdd57")
        painter.setPen(QPen(peak_color, 2))
        painter.drawLine(2, peak_y, width - 2, peak_y)

class AudioTranscriber(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transcritor de Áudio")
        self.setMinimumSize(800, 600)
        
        # Configuração dos diretórios
        self.audio_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
        self.transcription_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcricoes")
        self.config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
        
        # Cria os diretórios se não existirem
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.transcription_dir, exist_ok=True)
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Carrega o valor economizado
        self.load_savings()
        
        # Configurações de gravação
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_vu_meter)
        
        # Configuração dos dispositivos de áudio
        self.input_devices = self.get_input_devices()
        self.selected_device = None
        
        # Interface principal
        self.setup_ui()
        
        # Timer para atualização do VU meter
        self.timer.start(50)  # Atualiza a cada 50ms
        
        # Carrega as configurações
        self.load_settings()

    def test_device(self, device_info):
        """Testa se um dispositivo de áudio está realmente disponível"""
        try:
            # Tenta apenas consultar o dispositivo sem abrir stream
            sd.query_devices(device_info['index'])
            return True
        except Exception:
            return False

    def get_input_devices(self):
        """Obtém lista de dispositivos de entrada disponíveis"""
        devices = []
        seen_names = set()  # Para evitar duplicatas
        try:
            device_list = sd.query_devices()
            default_device = sd.query_devices(kind='input')
            
            for i, device in enumerate(device_list):
                # Evita duplicatas pelo nome
                if device['name'] in seen_names:
                    continue
                    
                if device['max_input_channels'] > 0:
                    seen_names.add(device['name'])
                    
                    # Usa taxa de amostragem padrão do dispositivo ou 44100 como fallback
                    samplerate = device.get('default_samplerate', 44100)
                    
                    device_info = {
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'samplerate': samplerate,
                        'is_default': (i == default_device['index'] if default_device else False)
                    }
                    
                    # Só adiciona se o dispositivo estiver realmente disponível
                    if self.test_device(device_info):
                        devices.append(device_info)
                    else:
                        print(f"Dispositivo ignorado (não disponível): {device['name']}")
                        
        except Exception as e:
            QMessageBox.warning(self, "Aviso", f"Erro ao listar dispositivos: {str(e)}")
            print(f"Detalhes do erro: {e}")  # Debug
            print("Dispositivos disponíveis:", sd.query_devices())  # Debug
        
        return devices

    def update_device_list(self):
        """Atualiza a lista de dispositivos no combobox"""
        try:
            self.device_combo.clear()
            self.input_devices = self.get_input_devices()
            
            if not self.input_devices:
                self.device_combo.addItem("Nenhum dispositivo encontrado")
                if hasattr(self, 'record_button'):
                    self.record_button.setEnabled(False)
                return
                
            # Adiciona dispositivos ao combo
            default_index = 0
            for i, device in enumerate(self.input_devices):
                device_name = device['name']
                if device['is_default']:
                    device_name += " (Padrão)"
                    default_index = i
                self.device_combo.addItem(f"{device_name} ({device['channels']} canais)")
            
            # Seleciona o dispositivo padrão
            self.device_combo.setCurrentIndex(default_index)
            
            if hasattr(self, 'record_button'):
                self.record_button.setEnabled(True)
                
        except Exception as e:
            print(f"Erro ao atualizar lista de dispositivos: {e}")  # Debug
            QMessageBox.warning(self, "Aviso", "Erro ao atualizar lista de dispositivos")

    def setup_ui(self):
        """Configura a interface principal"""
        # Configuração da janela principal
        self.setWindowTitle("Transcritor de Áudio")
        self.setMinimumSize(800, 600)
        
        # Define o estilo global - Dark Theme usando as cores de referência
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;  /* Background */
            }
            QWidget {
                background-color: #121212;
                color: #FFFFFF;  /* Primary text */
            }
            QTabWidget::pane {
                border: 1px solid #404040;  /* Top gradient */
                background: #121212;
                border-radius: 4px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background: #181818;  /* Menu bar */
                color: #B3B3B3;  /* Secondary text */
                padding: 12px 16px;
                border: 1px solid #404040;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 100px;
                font-size: 14px;
            }
            QTabBar::tab:hover {
                background: #282828;  /* Bottom gradient */
                color: #FFFFFF;  /* Primary text */
            }
            QTabBar::tab:selected {
                background: #282828;  /* Bottom gradient */
                color: #FFFFFF;  /* Primary text */
                border-bottom: none;
                font-weight: 500;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QLabel {
                color: #FFFFFF;  /* Primary text */
            }
            QPushButton {
                background-color: #282828;  /* Bottom gradient */
                color: #FFFFFF;  /* Primary text */
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #404040;  /* Top gradient */
            }
            QPushButton:pressed {
                background-color: #181818;  /* Menu bar */
            }
            QProgressBar {
                border: 1px solid #404040;  /* Top gradient */
                border-radius: 4px;
                text-align: center;
                color: #FFFFFF;  /* Primary text */
                background-color: #181818;  /* Menu bar */
            }
            QProgressBar::chunk {
                background-color: #404040;  /* Top gradient */
                border-radius: 3px;
            }
            QComboBox {
                background-color: #181818;  /* Menu bar */
                color: #FFFFFF;  /* Primary text */
                border: 1px solid #404040;  /* Top gradient */
                border-radius: 4px;
                padding: 5px 10px;
            }
            QComboBox:hover {
                border-color: #282828;  /* Bottom gradient */
            }
            QComboBox:focus {
                border-color: #404040;  /* Top gradient */
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #B3B3B3;  /* Secondary text */
                margin-right: 8px;
            }
            QTableWidget {
                background-color: #181818;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #FFFFFF;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #282828;
                color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #282828;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #404040;
            }
            QHeaderView::section:hover {
                background-color: #404040;
            }
            QLineEdit, QTextEdit {
                background-color: #181818;  /* Menu bar */
                color: #FFFFFF;  /* Primary text */
                border: 1px solid #404040;  /* Top gradient */
                border-radius: 4px;
                padding: 5px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #282828;  /* Bottom gradient */
            }
            QRadioButton {
                color: #FFFFFF;  /* Primary text */
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #404040;  /* Top gradient */
            }
            QRadioButton::indicator:checked {
                background-color: #282828;  /* Bottom gradient */
                border: 2px solid #282828;
            }
            QRadioButton::indicator:unchecked:hover {
                border: 2px solid #282828;  /* Bottom gradient */
            }
        """)
        
        # Widget central e layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Rodapé com economia
        self.savings_label = QLabel()
        self.savings_label.setStyleSheet("color: #2ecc71; padding: 5px;")
        self.update_savings_display()
        layout.addWidget(self.savings_label)
        
        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Tab de Gravação
        recording_tab = self.setup_recording_tab()
        self.tabs.addTab(recording_tab, "Gravação")
        
        # Tab de Transcrição
        transcription_tab = self.setup_transcription_tab()
        self.tabs.addTab(transcription_tab, "Transcrição")
        
        # Tab de Configurações
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Título da seção
        title_label = QLabel("Configuração dos Modelos Whisper")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        settings_layout.addWidget(title_label)
        
        # Descrição
        description = QLabel(
            "Selecione o modelo que deseja usar para transcrição. "
            "Modelos maiores oferecem melhor qualidade, mas requerem mais memória e processamento."
        )
        description.setWordWrap(True)
        description.setStyleSheet("margin-bottom: 15px;")
        settings_layout.addWidget(description)
        
        # Frame para os modelos
        models_frame = QFrame()
        models_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        models_frame.setLineWidth(1)
        models_frame.setStyleSheet("""
            QFrame {
                background-color: #282828;
                border-radius: 4px;
            }
        """)
        
        models_layout = QVBoxLayout(models_frame)
        
        # Definição dos modelos
        self.model_radios = {}
        self.model_group = QButtonGroup(self)  # Grupo para garantir seleção única
        
        self.models_info = [
            {
                'name': 'Tiny',
                'key': 'tiny',
                'size': '(39MB)',
                'description': 'Modelo mais rápido e leve, ideal para testes e transcrições simples. Menor precisão, mas excelente performance.',
                'color': '#FF6B6B'  # Vermelho
            },
            {
                'name': 'Small',
                'key': 'small',
                'size': '(142MB)',
                'description': 'Equilíbrio entre velocidade e precisão. Recomendado para a maioria dos casos.',
                'color': '#FF9F1C'  # Laranja
            },
            {
                'name': 'Base',
                'key': 'base',
                'size': '(466MB)',
                'description': 'Maior precisão que o Small, mantendo boa performance. Ideal para uso profissional.',
                'color': '#FFD93D'  # Amarelo
            },
            {
                'name': 'Medium',
                'key': 'medium',
                'size': '(1.5GB)',
                'description': 'Alta precisão e excelente reconhecimento de contexto. Requer mais recursos computacionais.',
                'color': '#4CAF50'  # Verde
            },
            {
                'name': 'Large',
                'key': 'large',
                'size': '(2.9GB)',
                'description': 'Máxima precisão e melhor compreensão de contexto. Requer hardware mais potente.',
                'color': '#2196F3'  # Azul
            }
        ]
        
        # Cria os widgets para cada modelo
        for model in self.models_info:
            model_container = QWidget()
            model_layout = QVBoxLayout(model_container)
            
            # Cabeçalho com nome e tamanho
            header_layout = QHBoxLayout()
            radio = QRadioButton(f"{model['name']} {model['size']}")
            radio.setStyleSheet(f"""
                QRadioButton {{
                    font-weight: bold;
                    color: {model['color']};
                }}
                QRadioButton::indicator {{
                    width: 13px;
                    height: 13px;
                    border-radius: 7px;
                    border: 2px solid {model['color']};
                }}
                QRadioButton::indicator:checked {{
                    background-color: {model['color']};
                    border: 2px solid {model['color']};
                }}
            """)
            
            # Adiciona o radio ao grupo
            self.model_group.addButton(radio)
            
            self.model_radios[model['key']] = {
                'radio': radio,
                'name': model['name']
            }
            
            header_layout.addWidget(radio)
            header_layout.addStretch()
            
            # Descrição do modelo
            description = QLabel(model['description'])
            description.setWordWrap(True)
            description.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    margin-top: 5px;
                    margin-bottom: 5px;
                    font-size: 12px;
                }
            """)
            model_layout.addLayout(header_layout)
            model_layout.addWidget(description)
            
            # Tamanho do modelo
            size_label = QLabel(model['size'])
            size_label.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    font-size: 12px;
                }
            """)
            model_layout.addWidget(size_label)
            
            # Adiciona uma linha separadora, exceto para o último item
            if model != self.models_info[-1]:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                separator.setStyleSheet("background-color: #404040;")
                separator.setMaximumHeight(1)
                model_layout.addWidget(separator)
            
            models_layout.addWidget(model_container)
        
        # Seleciona o modelo base por padrão
        self.model_radios['base']['radio'].setChecked(True)
        
        settings_layout.addWidget(models_frame)
        settings_layout.addStretch()
        
        # Botão de salvar configurações
        save_settings_button = QPushButton("Salvar Configurações")
        save_settings_button.clicked.connect(self.save_settings)
        save_settings_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        settings_layout.addWidget(save_settings_button)
        
        self.tabs.addTab(settings_tab, "Configurações")
        
        self.load_settings()
    
    def setup_recording_tab(self):
        """Configura a aba de gravação"""
        recording_tab = QWidget()
        recording_layout = QVBoxLayout(recording_tab)
        recording_layout.setContentsMargins(20, 20, 20, 20)
        recording_layout.setSpacing(15)
        
        # Seleção de dispositivo de entrada - Bulma select
        device_layout = QHBoxLayout()
        device_label = QLabel("Microfone:")
        device_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 500;
            }
        """)
        device_layout.addWidget(device_label)
        
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(300)
        self.device_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                background-color: #282828;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
            }
            QComboBox:hover {
                background-color: #404040;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #B3B3B3;
                margin-right: 8px;
            }
        """)
        device_layout.addWidget(self.device_combo)
        recording_layout.addLayout(device_layout)
        
        # Botões de controle com ícones Font Awesome
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.record_button = QPushButton(" Gravar")
        self.record_button.setIcon(qta.icon('fa5s.microphone'))
        self.record_button.setIconSize(QSize(20, 20))
        self.record_button.clicked.connect(self.toggle_recording)
        self.record_button.setMinimumHeight(40)
        self.record_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
                border: none;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #ff3860;
            }
            QPushButton:checked:hover {
                background-color: #ff2b56;
            }
        """)
        control_layout.addWidget(self.record_button)
        
        # Agora que o record_button foi criado, podemos atualizar a lista de dispositivos
        self.update_device_list()
        
        # Conecta o evento de mudança de dispositivo depois de popular a lista
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        
        self.upload_button = QPushButton(" Carregar")
        self.upload_button.setIcon(qta.icon('fa5s.file-upload'))
        self.upload_button.setIconSize(QSize(20, 20))
        self.upload_button.clicked.connect(self.upload_audio)
        self.upload_button.setMinimumHeight(40)
        self.upload_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
                border: none;
            }
            QPushButton:hover {
                background-color: #404040;
            }
        """)
        control_layout.addWidget(self.upload_button)
        control_layout.addStretch()
        
        recording_layout.addLayout(control_layout)
        
        # VU Meter com estilo Bulma
        self.vu_meter = VUMeter()
        self.vu_meter.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 6px;
            padding: 10px;
            margin: 10px 0;
        """)
        recording_layout.addWidget(self.vu_meter)
        
        # Lista de arquivos de áudio
        self.audio_list = QTableWidget()
        self.audio_list.setColumnCount(4)
        
        # Cria os cabeçalhos com ícones
        file_header = QTableWidgetItem(qta.icon('fa5s.file-audio'), " Nome do Arquivo")
        date_header = QTableWidgetItem(qta.icon('fa5s.calendar'), " Data de Criação")
        duration_header = QTableWidgetItem(qta.icon('fa5s.clock'), " Duração")
        delete_header = QTableWidgetItem(qta.icon('fa5s.trash-alt'), " Excluir")
        
        # Define os cabeçalhos
        self.audio_list.setHorizontalHeaderItem(0, file_header)
        self.audio_list.setHorizontalHeaderItem(1, date_header)
        self.audio_list.setHorizontalHeaderItem(2, duration_header)
        self.audio_list.setHorizontalHeaderItem(3, delete_header)
        
        # Configura o redimensionamento das colunas
        self.audio_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.audio_list.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.audio_list.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.audio_list.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.audio_list.horizontalHeader().setStyleSheet("""
            QTableWidget {
                background-color: #181818;
                border: 1px solid #404040;
                border-radius: 4px;
                color: #FFFFFF;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #282828;
                color: #FFFFFF;
            }
            QTableWidget::item:hover {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #282828;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #404040;
            }
            QHeaderView::section:hover {
                background-color: #404040;
            }
        """)
        self.audio_list.verticalHeader().hide()
        self.audio_list.setSelectionBehavior(QTableWidget.SelectRows)
        self.audio_list.setSelectionMode(QTableWidget.SingleSelection)
        self.audio_list.itemClicked.connect(self.select_audio_file)
        recording_layout.addWidget(self.audio_list)
        
        # Atualiza a lista de arquivos
        self.update_audio_list()
        
        return recording_tab

    def start_recording(self):
        """Inicia a gravação de áudio"""
        try:
            if not self.input_devices:
                raise Exception("Nenhum dispositivo de entrada disponível")
                
            device_index = self.device_combo.currentIndex()
            if device_index < 0 or device_index >= len(self.input_devices):
                raise Exception("Dispositivo inválido selecionado")
                
            device = self.input_devices[device_index]
            
            # Configurações otimizadas
            SAMPLE_RATE = 44100
            CHANNELS = 1
            DTYPE = 'float32'
            
            # Verifica se o dispositivo suporta a taxa de amostragem
            device_info = sd.query_devices(device['index'])
            if device_info['max_input_channels'] < CHANNELS:
                raise Exception(f"Dispositivo não suporta {CHANNELS} canais")
                
            # Usa a taxa de amostragem nativa do dispositivo se disponível
            if 'default_samplerate' in device_info:
                SAMPLE_RATE = int(device_info['default_samplerate'])
            
            self.audio_data = []
            self.stream = sd.InputStream(
                device=device['index'],
                channels=CHANNELS,
                samplerate=SAMPLE_RATE,
                dtype=DTYPE,
                callback=self.audio_callback,
                blocksize=1024,  # Tamanho do buffer menor para menor latência
                latency='low'    # Baixa latência
            )
            
            # Armazena as configurações para uso posterior
            self.current_sample_rate = SAMPLE_RATE
            
            self.stream.start()
            self.recording = True
            self.record_button.setText(" Parar")
            
        except Exception as e:
            error_msg = str(e)
            if "Invalid device" in error_msg:
                error_msg = "Dispositivo de áudio inválido ou não disponível. Tente selecionar outro dispositivo."
            elif "Input overflow" in error_msg:
                error_msg = "Erro de buffer do microfone. Tente diminuir a taxa de amostragem."
            
            print(f"Erro detalhado: {e}")  # Debug
            QMessageBox.warning(self, "Erro", f"Erro ao iniciar gravação: {error_msg}")
            self.recording = False
            self.record_button.setText(" Gravar")

    def stop_recording(self):
        """Para a gravação de áudio"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                self.stream = None
                
                if self.audio_data:
                    # Concatena os dados do áudio
                    audio_data = np.concatenate(self.audio_data, axis=0)
                    
                    # Normaliza o volume se necessário
                    max_val = np.max(np.abs(audio_data))
                    if max_val > 0:
                        audio_data = audio_data / max_val
                    
                    # Salva o arquivo
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{self.audio_dir}/gravacao_{timestamp}.wav"
                    
                    # Garante que o diretório existe
                    os.makedirs(self.audio_dir, exist_ok=True)
                    
                    # Salva com a taxa de amostragem correta
                    sf.write(filename, audio_data, self.current_sample_rate, 'PCM_16')
                    
                    # Atualiza a interface
                    self.current_audio_file = filename
                    self.update_selected_file_label(filename)
                    self.transcribe_button.setEnabled(True)
                    self.update_audio_list()
                    
                    QMessageBox.information(self, "Sucesso", f"Áudio salvo como {os.path.basename(filename)}")
            
            except Exception as e:
                print(f"Erro ao salvar áudio: {e}")
                QMessageBox.critical(self, "Erro", f"Erro ao salvar a gravação: {str(e)}")
        
        self.recording = False
        self.record_button.setText(" Gravar")

    def toggle_recording(self):
        """Inicia ou para a gravação de áudio"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def audio_callback(self, indata, frames, time, status):
        """Callback para processar os dados de áudio"""
        if status:
            print(status)
        self.audio_data.append(indata.copy())
        self.update_vu_meter()

    def update_vu_meter(self):
        """Atualiza o VU meter"""
        if self.recording and self.audio_data:
            # Pega os últimos samples para calcular o volume
            last_samples = self.audio_data[-1] if self.audio_data else np.zeros(1000)
            
            # Calcula RMS do áudio
            rms = np.sqrt(np.mean(last_samples**2))
            
            # Atualiza o VU meter
            self.vu_meter.set_value(rms)

    def update_audio_list(self):
        """Atualiza a lista de arquivos de áudio disponíveis"""
        self.audio_list.setRowCount(0)
        for file in os.listdir(self.audio_dir):
            if file.endswith((".wav", ".mp3", ".m4a")):
                file_path = os.path.join(self.audio_dir, file)
                # Obtém a data de criação
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                creation_str = creation_time.strftime("%d/%m/%Y %H:%M")
                
                # Obtém a duração do áudio
                try:
                    audio_info = sf.info(file_path)
                    duration = audio_info.duration
                    duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"
                except Exception as e:
                    print(f"Erro ao ler duração do arquivo {file}: {e}")
                    duration_str = "??:??"
                
                # Adiciona uma nova linha
                row = self.audio_list.rowCount()
                self.audio_list.insertRow(row)
                
                # Adiciona os itens
                self.audio_list.setItem(row, 0, QTableWidgetItem(file))
                self.audio_list.setItem(row, 1, QTableWidgetItem(creation_str))
                
                # Adiciona a duração centralizada
                duration_item = QTableWidgetItem(duration_str)
                duration_item.setTextAlignment(Qt.AlignCenter)
                self.audio_list.setItem(row, 2, duration_item)
                
                # Adiciona o botão de exclusão
                delete_button = QPushButton()
                delete_button.setIcon(qta.icon('fa5s.trash-alt'))
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                        border-radius: 3px;
                    }
                """)
                delete_button.clicked.connect(lambda checked, f=file: self.confirm_delete_audio(f))
                self.audio_list.setCellWidget(row, 3, delete_button)

    @Slot()
    def select_audio_file(self, item):
        """Seleciona um arquivo de áudio para transcrição"""
        row = item.row()
        filename = self.audio_list.item(row, 0).text()
        self.current_audio_file = f"{self.audio_dir}/{filename}"
        self.update_selected_file_label(self.current_audio_file)
        self.transcribe_button.setEnabled(True)

    def setup_transcription_tab(self):
        """Configura a aba de transcrição"""
        transcription_tab = QWidget()
        transcription_layout = QVBoxLayout(transcription_tab)
        transcription_layout.setContentsMargins(20, 20, 20, 20)
        transcription_layout.setSpacing(15)
        
        # Container para o nome do arquivo
        file_container = QWidget()
        file_container.setStyleSheet("""
            QWidget {
                background-color: #282828;
                border-radius: 6px;
                padding: 15px;
                margin: 10px;
            }
        """)
        file_layout = QHBoxLayout()
        file_layout.setAlignment(Qt.AlignCenter)  # Centraliza o conteúdo horizontalmente
        file_container.setLayout(file_layout)
        
        # Label "Arquivo:"
        arquivo_label = QLabel("Arquivo:")
        arquivo_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                margin-right: 5px;
            }
        """)
        arquivo_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        file_layout.addWidget(arquivo_label)
        
        # Nome do arquivo
        self.filename_label = QLabel()
        self.filename_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-weight: bold;
                margin-left: 5px;
            }
        """)
        self.filename_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        file_layout.addWidget(self.filename_label)
        
        transcription_layout.addWidget(file_container)
        
        # Botão de transcrição com ícone
        self.transcribe_button = QPushButton(" Transcrever")
        self.transcribe_button.setIcon(qta.icon('fa5s.language'))
        self.transcribe_button.setIconSize(QSize(20, 20))
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setMinimumHeight(40)
        self.transcribe_button.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
                border: none;
            }
            QPushButton:hover:enabled {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #181818;
                color: #B3B3B3;
            }
        """)
        
        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #404040;
                border-radius: 4px;
                text-align: center;
                color: #FFFFFF;
                background-color: #181818;
            }
            QProgressBar::chunk {
                background-color: #404040;
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()
        
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.addWidget(self.transcribe_button)
        buttons_layout.addWidget(self.progress_bar)
        
        transcription_layout.addWidget(buttons_container)
        
        # Campo de texto para a transcrição
        self.transcription_text = QTextEdit()
        self.transcription_text.setReadOnly(True)
        self.transcription_text.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        transcription_layout.addWidget(self.transcription_text)
        
        # Container para os botões de exportação
        export_container = QWidget()
        export_layout = QHBoxLayout()
        export_container.setLayout(export_layout)
        
        # Estilo comum para os botões
        button_style = """
            QPushButton {
                padding: 8px 20px;
                font-size: 14px;
                font-weight: 500;
                border-radius: 4px;
                background-color: #282828;
                color: #FFFFFF;
                border: none;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:disabled {
                background-color: #181818;
                color: #B3B3B3;
            }
        """
        
        # Botão TXT
        self.txt_button = QPushButton(".TXT")
        self.txt_button.setStyleSheet(button_style)
        self.txt_button.clicked.connect(self.export_txt)
        self.txt_button.setEnabled(False)
        export_layout.addWidget(self.txt_button)
        
        # Botão DOCX
        self.docx_button = QPushButton(".DOCX")
        self.docx_button.setStyleSheet(button_style)
        self.docx_button.clicked.connect(self.export_docx)
        self.docx_button.setEnabled(False)
        export_layout.addWidget(self.docx_button)
        
        # Botão Copiar
        self.copy_button = QPushButton(" Copiar")
        self.copy_button.setIcon(qta.icon('fa5s.copy'))
        self.copy_button.setIconSize(QSize(16, 16))
        self.copy_button.setStyleSheet(button_style)
        self.copy_button.clicked.connect(self.copy_transcription)
        self.copy_button.setEnabled(False)
        export_layout.addWidget(self.copy_button)
        
        transcription_layout.addWidget(export_container)
        
        return transcription_tab

    @Slot()
    def start_transcription(self):
        """Inicia o processo de transcrição"""
        if not self.current_audio_file:
            QMessageBox.warning(self, "Aviso", "Selecione um arquivo de áudio primeiro!")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        try:
            import whisper
            import soundfile as sf
            
            # Atualiza o status
            self.progress_bar.setValue(10)
            self.transcription_text.setText("Carregando modelo Whisper...")
            
            # Usa o modelo selecionado nas configurações
            model_key, model_name = self.get_selected_model()
            
            # Carrega o modelo selecionado
            model = whisper.load_model(model_key)
            
            self.progress_bar.setValue(30)
            self.transcription_text.setText("Transcrevendo áudio...\nIsso pode levar alguns segundos.")
            
            # Obtém a duração real do arquivo de áudio
            audio_info = sf.info(self.current_audio_file)
            duration_seconds = audio_info.duration
            
            # Calcula o custo estimado
            estimated_cost = self.calculate_transcription_cost(duration_seconds)
            
            # Atualiza o total economizado
            self.total_savings += estimated_cost
            self.save_savings()
            self.update_savings_display()
            
            # Configurações otimizadas para PT-BR
            result = model.transcribe(
                self.current_audio_file,
                language="pt",
                task="transcribe",
                initial_prompt="Transcrição em português brasileiro:",
                temperature=0.2,  # Menor temperatura para maior precisão
                best_of=2,        # Tenta 2 vezes e pega o melhor resultado
            )
            
            # Formata o texto para melhor legibilidade
            transcribed_text = result["text"].strip()
            formatted_text = f"""Transcrição concluída:

{transcribed_text}

---
Modelo utilizado: {model_name}
Idioma: Português (Brasil)
Duração do áudio: {duration_seconds:.2f} segundos
Preço estimado da transcrição: ${estimated_cost:.3f}"""
            
            # Mostra o resultado
            self.progress_bar.setValue(100)
            self.transcription_text.setText(formatted_text)
            
            # Atualiza os botões de exportação
            self.update_export_buttons(True)
            
            QMessageBox.information(self, "Sucesso", "Transcrição concluída com sucesso!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao transcrever: {str(e)}")
            self.progress_bar.setVisible(False)

    @Slot()
    def export_txt(self):
        """Exporta a transcrição como arquivo TXT"""
        if not self.transcription_text.toPlainText():
            return
            
        filename = QFileDialog.getSaveFileName(
            self,
            "Exportar como TXT",
            os.path.splitext(self.current_audio_file)[0] + ".txt",
            "Arquivo de texto (*.txt)"
        )[0]
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.transcription_text.toPlainText())
                QMessageBox.information(self, "Sucesso", "Arquivo TXT exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar arquivo: {str(e)}")

    @Slot()
    def export_docx(self):
        """Exporta a transcrição como arquivo DOCX"""
        if not self.transcription_text.toPlainText():
            return
            
        filename = QFileDialog.getSaveFileName(
            self,
            "Exportar como DOCX",
            os.path.splitext(self.current_audio_file)[0] + ".docx",
            "Documento Word (*.docx)"
        )[0]
        
        if filename:
            try:
                from docx import Document
                doc = Document()
                doc.add_paragraph(self.transcription_text.toPlainText())
                doc.save(filename)
                QMessageBox.information(self, "Sucesso", "Arquivo DOCX exportado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar arquivo: {str(e)}")

    @Slot()
    def copy_transcription(self):
        """Copia a transcrição para a área de transferência"""
        if self.transcription_text.toPlainText():
            # Extrai apenas o texto transcrito (remove o cabeçalho e as informações do modelo)
            text = self.transcription_text.toPlainText()
            transcribed_text = text.split("---")[0].strip()
            
            # Remove "Transcrição concluída:" e espaços extras
            if transcribed_text.startswith("Transcrição concluída:"):
                transcribed_text = transcribed_text.replace("Transcrição concluída:", "").strip()
            
            clipboard = QApplication.clipboard()
            clipboard.setText(transcribed_text)
            
            # Feedback visual temporário
            original_text = self.copy_button.text()
            self.copy_button.setText(" Copiado!")
            QTimer.singleShot(2000, lambda: self.copy_button.setText(original_text))

    def update_export_buttons(self, enable=True):
        """Atualiza o estado dos botões de exportação"""
        self.txt_button.setEnabled(enable)
        self.docx_button.setEnabled(enable)
        self.copy_button.setEnabled(enable)

    def save_settings(self):
        """Salva as configurações em um arquivo JSON"""
        model_key, _ = self.get_selected_model()
        settings = {
            'selected_model': model_key
        }
        
        with open(f'{self.config_dir}/whisper_settings.json', 'w') as f:
            json.dump(settings, f)
        
        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")

    def load_settings(self):
        """Carrega as configurações do arquivo JSON"""
        try:
            with open(f'{self.config_dir}/whisper_settings.json', 'r') as f:
                settings = json.load(f)
                selected_model = settings.get('selected_model', 'base')
                
                # Marca o radio do modelo salvo
                if selected_model in self.model_radios:
                    self.model_radios[selected_model]['radio'].setChecked(True)
        except FileNotFoundError:
            # Se não houver arquivo de configuração, usa o modelo base
            self.model_radios['base']['radio'].setChecked(True)

    def get_selected_model(self):
        """Retorna a chave e o nome do modelo selecionado"""
        for key, data in self.model_radios.items():
            if data['radio'].isChecked():
                return key, data['name']
        return 'base', 'Base'  # Modelo padrão se nenhum estiver selecionado

    def load_savings(self):
        """Carrega o valor total economizado"""
        try:
            with open(f'{self.config_dir}/savings.json', 'r') as f:
                data = json.load(f)
                self.total_savings = data.get('total_savings', 0.0)
        except FileNotFoundError:
            self.total_savings = 0.0

    def save_savings(self):
        """Salva o valor total economizado"""
        with open(f'{self.config_dir}/savings.json', 'w') as f:
            json.dump({'total_savings': self.total_savings}, f)

    def update_savings_display(self):
        """Atualiza o display de economia"""
        self.savings_label.setText(f"Você economizou ${self.total_savings:.2f} usando nossa aplicação!")

    def calculate_transcription_cost(self, duration_seconds):
        """Calcula o custo estimado da transcrição"""
        # Converte segundos para minutos e multiplica pelo custo por minuto
        cost = (duration_seconds / 60) * 0.006
        return cost

    def upload_audio(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Áudio",
            "",
            "Arquivos de Áudio (*.wav *.mp3 *.m4a)"
        )
        if file_name:
            dest_path = f"{self.audio_dir}/{os.path.basename(file_name)}"
            import shutil
            shutil.copy2(file_name, dest_path)
            QMessageBox.information(self, "Sucesso", f"Arquivo importado: {os.path.basename(dest_path)}")
            self.update_audio_list()
            
            # Seleciona automaticamente o arquivo importado
            self.current_audio_file = dest_path
            self.update_selected_file_label(dest_path)
            self.transcribe_button.setEnabled(True)

    def on_device_changed(self, text):
        """Chamado quando o usuário muda o dispositivo de entrada"""
        if self.recording:
            self.stop_recording()
            self.start_recording()

    def update_selected_file_label(self, filename):
        """Atualiza o label do arquivo selecionado"""
        if filename:
            self.filename_label.setText(os.path.basename(filename))
        else:
            self.filename_label.setText("")

    def confirm_delete_audio(self, filename):
        """Mostra um diálogo de confirmação antes de excluir o arquivo"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Confirmar Exclusão")
        msg.setText(f"Tem certeza que deseja excluir o arquivo '{filename}'?")
        msg.setInformativeText("Esta ação não pode ser desfeita.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        # Traduz os botões
        msg.button(QMessageBox.Yes).setText("Sim")
        msg.button(QMessageBox.No).setText("Não")
        
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #282828;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #404040;
                color: #FFFFFF;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        
        if msg.exec_() == QMessageBox.Yes:
            try:
                os.remove(os.path.join(self.audio_dir, filename))
                self.update_audio_list()
            except Exception as e:
                error_msg = QMessageBox()
                error_msg.setIcon(QMessageBox.Critical)
                error_msg.setWindowTitle("Erro")
                error_msg.setText(f"Erro ao excluir o arquivo: {str(e)}")
                error_msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #282828;
                    }
                    QMessageBox QLabel {
                        color: #FFFFFF;
                    }
                    QPushButton {
                        background-color: #404040;
                        color: #FFFFFF;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #505050;
                    }
                """)
                error_msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Aplicar estilo moderno
    app.setStyle('Fusion')
    
    window = AudioTranscriber()
    window.show()
    sys.exit(app.exec())