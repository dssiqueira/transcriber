"""
Modern UI design for the transcriber application.
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QTextEdit, QComboBox, QFrame, QSizePolicy, QSpacerItem,
                             QProgressDialog, QMessageBox, QDialog, QProgressBar,
                             QStackedWidget, QScrollArea)
from PySide6.QtCore import Qt, QThread, QObject, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPainter, QPen, QColor, QBrush
import qtawesome as qta
import logging

from .styles import COLORS
from src.core.config import ConfigManager
from src.core.audio import AudioRecorder, AudioFileManager
from src.core.transcription import TranscriptionEngine, TranscriptionHistory


class ModernProgressDialog(QDialog):
    """Custom progress dialog that matches the application's modern design."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transcrição em Andamento")
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Transcrevendo áudio...")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Apply minimal styling to avoid layout conflicts
        self.setStyleSheet(f"""
            ModernProgressDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
            QProgressBar {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['primary']};
            }}
        """)


class ModernCard(QFrame):
    """Modern card component with rounded corners and shadow effect."""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(f"""
            ModernCard {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
                margin: 8px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        if title:
            title_label = QLabel(title)
            title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            title_label.setStyleSheet(f"color: {COLORS['primary_text']}; margin-bottom: 8px;")
            layout.addWidget(title_label)
        
        self.content_layout = layout
    
    def add_widget(self, widget):
        """Add widget to card content."""
        self.content_layout.addWidget(widget)


class ModernButton(QPushButton):
    """Modern button with hover effects."""
    
    def __init__(self, text, icon=None, style="primary", parent=None):
        super().__init__(text, parent)
        
        if icon:
            self.setIcon(qta.icon(icon, color=COLORS['text']))
        
        color_map = {
            'primary': COLORS['accent'],
            'success': COLORS['success'],
            'danger': COLORS['danger'],
            'secondary': COLORS['secondary']
        }
        
        bg_color = color_map.get(style, COLORS['accent'])
        hover_color = self._darken_color(bg_color, 0.8)
        
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {bg_color};
                color: {COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            ModernButton:hover {{
                background-color: {hover_color};
            }}
            ModernButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.6)};
            }}
            ModernButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['secondary_text']};
            }}
        """)
    
    def set_style(self, style="primary"):
        """Set the button style dynamically."""
        color_map = {
            'primary': COLORS['accent'],
            'success': COLORS['success'],
            'danger': COLORS['danger'],
            'secondary': COLORS['secondary']
        }
        
        bg_color = color_map.get(style, COLORS['accent'])
        hover_color = self._darken_color(bg_color, 0.8)
        
        self.setStyleSheet(f"""
            ModernButton {{
                background-color: {bg_color};
                color: {COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            ModernButton:hover {{
                background-color: {hover_color};
            }}
            ModernButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.6)};
            }}
            ModernButton:disabled {{
                background-color: {COLORS['border']};
                color: {COLORS['secondary_text']};
            }}
        """)

    def _darken_color(self, color, factor):
        """Darken a color by a factor."""
        color = QColor(color)
        return f"rgba({int(color.red() * factor)}, {int(color.green() * factor)}, {int(color.blue() * factor)}, {color.alpha()})"


class WaveformWidget(QWidget):
    """Modern waveform visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            WaveformWidget {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        
        self.audio_data = []
        self.is_recording = False
    
    def paintEvent(self, event):
        """Paint the waveform with real audio levels."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(COLORS['surface']))
        
        if self.is_recording and hasattr(self, 'audio_levels') and self.audio_levels:
            # Draw modern waveform bars with gradient colors
            width = self.width()
            height = self.height()
            center_y = height // 2
            
            # Calculate bar dimensions to fill entire space
            num_bars = len(self.audio_levels)
            bar_width = max(3, (width - 10) // num_bars - 1)  # Reduced margins, increased bar width
            spacing = (width - 10) // num_bars
            start_x = 5  # Smaller margin
            
            for i in range(num_bars):
                x = start_x + i * spacing
                # Scale audio level to bar height with full range
                level = min(1.0, max(0.0, self.audio_levels[i]))
                min_height = 6
                max_height = height - 10  # Use almost full height
                bar_height = int(min_height + level * (max_height - min_height))
                
                # Neon gradient based on audio level
                if level < 0.2:
                    # Very low levels - azul neon
                    color = QColor(0, 187, 249)  # #00BBF9
                elif level < 0.4:
                    # Low levels - ciano neon
                    color = QColor(0, 245, 212)  # #00F5D4
                elif level < 0.6:
                    # Medium levels - amarelo neon
                    color = QColor(254, 228, 64)  # #FEE440
                elif level < 0.8:
                    # High levels - rosa neon
                    color = QColor(241, 91, 181)  # #F15BB5
                else:
                    # Peak levels - roxo neon
                    color = QColor(155, 93, 229)  # #9B5DE5
                
                painter.setPen(QPen(color, 0))
                painter.setBrush(QBrush(color))
                painter.drawRect(x, center_y - bar_height // 2, bar_width, bar_height)
        elif self.is_recording:
            # Fallback animated bars if no audio data
            painter.setPen(QColor(COLORS['accent']))
            painter.setBrush(QBrush(QColor(COLORS['accent'])))
            
            width = self.width()
            height = self.height()
            center_y = height // 2
            
            import random
            for i in range(0, width, 5):
                bar_height = random.randint(15, height - 30)
                painter.drawRect(i, center_y - bar_height // 2, 3, bar_height)
    
    def start_recording(self):
        """Start recording animation."""
        self.is_recording = True
        self.audio_levels = []
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_waveform)
        self.timer.start(50)  # Faster updates for smoother animation
    
    def _update_waveform(self):
        """Update waveform with real audio data from recorder."""
        try:
            # Check if we have direct reference to audio recorder
            if (hasattr(self, 'audio_recorder') and 
                self.audio_recorder.recording and 
                hasattr(self.audio_recorder, 'audio_data') and 
                self.audio_recorder.audio_data):
                
                import numpy as np
                
                # Get the most recent audio data
                recent_chunks = self.audio_recorder.audio_data[-3:] if len(self.audio_recorder.audio_data) >= 3 else self.audio_recorder.audio_data
                
                if recent_chunks:
                    # Combine recent chunks
                    combined_data = np.concatenate(recent_chunks, axis=0)
                    
                    # Flatten if stereo
                    if len(combined_data.shape) > 1:
                        combined_data = np.mean(combined_data, axis=1)
                    
                    # Process into bars for waveform
                    if len(combined_data) > 0:
                        # Use smaller chunks for more responsive visualization
                        num_bars = 80
                        chunk_size = max(1, len(combined_data) // num_bars)
                        new_levels = []
                        
                        for i in range(0, min(len(combined_data), num_bars * chunk_size), chunk_size):
                            chunk = combined_data[i:i+chunk_size]
                            if len(chunk) > 0:
                                # Calculate RMS level
                                rms = np.sqrt(np.mean(chunk**2))
                                # Amplify significantly for visibility
                                level = min(1.0, rms * 50)
                                new_levels.append(level)
                        
                        # Ensure we have enough levels
                        while len(new_levels) < num_bars:
                            new_levels.append(0.0)
                        
                        self.audio_levels = new_levels[:num_bars]
                    else:
                        self.audio_levels = [0.0] * 80
                else:
                    self.audio_levels = [0.0] * 80
            else:
                # Animated pattern when not recording
                import random
                import math
                import time
                
                t = time.time() * 2
                new_levels = []
                for i in range(80):
                    base_level = (math.sin(t + i * 0.2) + 1) / 2
                    noise = random.uniform(-0.15, 0.15)
                    level = max(0.05, min(0.7, base_level + noise))
                    new_levels.append(level)
                
                self.audio_levels = new_levels
                
        except Exception as e:
            # Simple fallback
            import random
            self.audio_levels = [random.uniform(0.1, 0.5) for _ in range(80)]
        
        self.update()
    
    def stop_recording(self):
        """Stop recording animation."""
        self.is_recording = False
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.update()


class FileListItem(QFrame):
    """Clickable widget representing a single file in the list."""
    
    clicked = Signal(str)
    
    def __init__(self, file_info, parent=None):
        super().__init__(parent)
        self.file_path = file_info['path']
        self._is_selected = False
        self.setup_ui(file_info)

    def setup_ui(self, file_info):
        self.setFrameShape(QFrame.NoFrame)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("selected", False)
        self.setStyleSheet(f"""
            FileListItem {{
                background-color: transparent;
                border-radius: 8px;
                border: 1px solid transparent;
                padding: 15px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            FileListItem:hover {{
                background-color: {COLORS['hover']};
            }}
            FileListItem[selected="true"] {{
                background-color: {COLORS['accent']};
                border-color: {COLORS['accent']};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(qta.icon('fa5s.file-audio', color=COLORS['accent']).pixmap(24, 24))
        self.icon_label.setStyleSheet("background-color: transparent;")
        layout.addWidget(self.icon_label)

        self.name_label = QLabel(file_info['name'])
        self.name_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

        self.duration_label = QLabel(str(self._format_duration(file_info.get('duration', 0))))
        self.size_label = QLabel(str(self._format_size(file_info.get('size', 0))))
        self.date_label = QLabel(self._format_date(file_info.get('modified', 0)))

        self.update_text_color(False)

        layout.addWidget(self.name_label, 3)
        layout.addStretch(1)
        layout.addWidget(self.duration_label)
        layout.addWidget(self.size_label)
        layout.addWidget(self.date_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.file_path)
        super().mousePressEvent(event)

    def set_selected(self, selected):
        self._is_selected = selected
        self.setProperty("selected", selected)
        self.update_text_color(selected)
        self.style().polish(self)

    def update_text_color(self, is_selected):
        primary_color = "white" if is_selected else COLORS['primary_text']
        secondary_color = "#e0e0e0" if is_selected else COLORS['secondary_text']
        
        self.name_label.setStyleSheet(f"color: {primary_color}; background-color: transparent;")
        for label in [self.duration_label, self.size_label, self.date_label]:
            label.setStyleSheet(f"color: {secondary_color}; font-size: 11px; background-color: transparent;")

    def _format_duration(self, seconds):
        if seconds is None:
            return "0.0s"
        if seconds < 60:
            return f"{seconds:.1f}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"

    def _format_date(self, timestamp):
        """Format timestamp to a readable date string."""
        if not timestamp:
            return "--"
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    def _format_size(self, size_bytes):
        if size_bytes == 0: return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class FileListWidget(QWidget):
    """Widget for displaying audio files in a scrollable list."""
    
    file_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_widgets = []
        self.selected_item = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the scrollable list UI."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setContentsMargins(0, 0, 10, 0)
        self.list_layout.setSpacing(0)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)

    def add_file(self, file_info):
        """Add a file item to the list."""
        file_item = FileListItem(file_info)
        file_item.clicked.connect(self._on_item_clicked)
        self.list_layout.insertWidget(self.list_layout.count() - 1, file_item)
        self.file_widgets.append(file_item)

    def _on_item_clicked(self, file_path):
        """Handle item selection and visual state."""
        for item in self.file_widgets:
            is_selected = (item.file_path == file_path)
            if is_selected:
                self.selected_item = item
            item.set_selected(is_selected)
        
        self.file_selected.emit(file_path)

    def clear_files(self):
        """Clear all file items from the list."""
        for widget in self.file_widgets:
            widget.deleteLater()
        self.file_widgets.clear()


class TranscriptionWorker(QObject):
    """Worker to run transcription in a separate thread."""
    transcription_completed = Signal(dict)
    transcription_failed = Signal(str)
    progress_updated = Signal(int, str)

    def __init__(self, transcription_engine, audio_file):
        super().__init__()
        self.transcription_engine = transcription_engine
        self.audio_file = audio_file

    def run(self):
        """Execute the transcription task."""
        import logging
        try:
            def progress_callback(value, message):
                self.progress_updated.emit(value, message)
            
            result = self.transcription_engine.transcribe_sync(
                self.audio_file, 
                progress_callback=progress_callback
            )
            logging.info(f"Transcription worker result: {result}")
            if result.get('success', False):
                self.transcription_completed.emit(result)
            else:
                self.transcription_failed.emit(result.get('error', 'Unknown error'))
        except Exception as e:
            import traceback
            logging.error(f"Error in transcription worker: {traceback.format_exc()}")
            self.transcription_failed.emit(str(e))

class ModernTranscriberWindow(QMainWindow):
    """Modern transcriber main window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcriber")
        self.setMinimumSize(1200, 800)
        
        # Set window icon
        from pathlib import Path
        from PySide6.QtGui import QIcon
        icon_path = Path(__file__).parent.parent.parent / "img" / "voice.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Initialize components with proper configuration
        from pathlib import Path
        from src.core.config import ConfigManager
        
        # Setup paths and config
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        AUDIO_DIR = PROJECT_ROOT / "audio"
        TRANSCRIPTIONS_DIR = PROJECT_ROOT / "transcriptions"
        AUDIO_DIR.mkdir(exist_ok=True)
        TRANSCRIPTIONS_DIR.mkdir(exist_ok=True)
        
        self.config_manager = ConfigManager()
        
        self.audio_recorder = AudioRecorder(str(AUDIO_DIR), self.config_manager.config.audio.__dict__)
        self.file_manager = AudioFileManager(str(AUDIO_DIR))
        self.transcription_engine = TranscriptionEngine(self.config_manager)
        self.transcription_history = TranscriptionHistory(str(TRANSCRIPTIONS_DIR))
        
        # Setup UI
        self._setup_ui()
        self._setup_connections()
        
        # Load initial data
        self._refresh_audio_files()
        self._populate_microphones()

    def _setup_ui(self):
        """Setup the modern UI with navigation."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main vertical layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation bar
        nav_bar = self._create_navigation_bar()
        main_layout.addWidget(nav_bar)
        
        # Content area with stacked widget
        self.content_stack = QStackedWidget()
        main_layout.addWidget(self.content_stack)
        
        # Create recording view
        recording_view = self._create_recording_view()
        self.content_stack.addWidget(recording_view)
        
        # Create files view
        files_view = self._create_files_view()
        self.content_stack.addWidget(files_view)
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
            }}
            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                font-family: "Segoe UI", sans-serif;
            }}
        """)
    
    def _create_navigation_bar(self):
        """Create the top navigation bar."""
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(20, 10, 20, 10)
        
        # Navigation buttons
        self.record_nav_btn = ModernButton("Record", "fa5s.microphone", "primary")
        self.files_nav_btn = ModernButton("My Files", "fa5s.folder", "secondary")
        self.settings_nav_btn = ModernButton("Settings", "fa5s.cog", "secondary")
        
        nav_layout.addWidget(self.record_nav_btn)
        nav_layout.addWidget(self.files_nav_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.settings_nav_btn)
        
        return nav_widget
    
    def _create_recording_view(self):
        """Create the recording view with proper layout."""
        view_widget = QWidget()
        main_layout = QVBoxLayout(view_widget)
        main_layout.setContentsMargins(50, 30, 50, 50)
        main_layout.setSpacing(0)
        
        # Waveform area - larger and centered
        self.waveform = WaveformWidget()
        self.waveform.setMinimumHeight(250)
        self.waveform.setMaximumHeight(250)
        self.waveform.setStyleSheet(f"""
            WaveformWidget {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 2px solid {COLORS['border']};
                margin: 20px 0px;
            }}
        """)
        main_layout.addWidget(self.waveform)
        
        # Add some space
        main_layout.addSpacing(30)
        
        # Recording timer - centered and prominent
        self.recording_status = QLabel("00:00:00")
        self.recording_status.setAlignment(Qt.AlignCenter)
        self.recording_status.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.recording_status.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['primary_text']};
                background-color: transparent;
                padding: 20px;
            }}
        """)
        main_layout.addWidget(self.recording_status)
        
        # Add flexible space
        main_layout.addStretch()
        
        # Bottom controls container
        controls_container = QWidget()
        controls_container.setFixedHeight(120)
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        
        # Microphone selector - left side
        from PySide6.QtWidgets import QComboBox
        self.mic_selector = QComboBox()
        self.mic_selector.setFixedSize(250, 45)
        self.mic_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: 10px;
                padding: 10px 15px;
                color: {COLORS['text']};
                font-size: 14px;
                font-weight: 500;
            }}
            QComboBox:hover {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid {COLORS['text']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        
        # Record button - center, large and prominent
        self.record_button = QPushButton("")
        self.record_button.setIcon(qta.icon("fa5s.circle"))
        self.record_button.setFixedSize(100, 100)
        self.record_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #ff4757;
                border: 4px solid #ff4757;
                border-radius: 50px;
                font-size: 32px;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #ff3742;
                border-color: #ff3742;
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background-color: #ff2731;
                border-color: #ff2731;
            }}
        """)
        
        # Layout the controls
        controls_layout.addWidget(self.mic_selector, 0, Qt.AlignLeft | Qt.AlignVCenter)
        controls_layout.addStretch()
        controls_layout.addWidget(self.record_button, 0, Qt.AlignCenter)
        controls_layout.addStretch()
        
        # Add empty widget for balance
        balance_widget = QWidget()
        balance_widget.setFixedSize(250, 45)
        controls_layout.addWidget(balance_widget, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        main_layout.addWidget(controls_container)
        
        return view_widget
    
    def _create_files_view(self):
        """Create the files view with a redesigned layout."""
        view_widget = QWidget()
        layout = QVBoxLayout(view_widget)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(25)
        
        # Files header
        header_layout = QHBoxLayout()
        files_title = QLabel("Meus Arquivos de Áudio")
        files_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        files_title.setStyleSheet(f"color: {COLORS['primary_text']}; margin-bottom: 5px;")
        
        header_layout.addWidget(files_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Container for file list and message
        self.files_container = QStackedWidget()
        layout.addWidget(self.files_container)

        # File list table
        self.file_list = FileListWidget()
        self.files_container.addWidget(self.file_list)

        # No files message
        self.no_files_label = QLabel("Nenhum arquivo de áudio encontrado.\nGrave um áudio para começar.")
        self.no_files_label.setAlignment(Qt.AlignCenter)
        self.no_files_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['secondary_text']};
                font-size: 16px;
                padding: 40px;
                background-color: {COLORS['surface']};
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        self.files_container.addWidget(self.no_files_label)

        # Transcription controls
        transcribe_layout = QHBoxLayout()
        transcribe_layout.addStretch()
        
        self.transcribe_button = ModernButton("Transcrever Selecionado", "fa5s.language", "primary")
        self.transcribe_button.setEnabled(False)
        self.transcribe_button.setMinimumSize(220, 50)
        
        transcribe_layout.addWidget(self.transcribe_button)
        layout.addLayout(transcribe_layout)
        
        return view_widget
    
    def _setup_connections(self):
        """Setup signal connections."""
        # Navigation
        self.record_nav_btn.clicked.connect(lambda: self._switch_view("recording"))
        self.files_nav_btn.clicked.connect(lambda: self._switch_view("files"))
        self.settings_nav_btn.clicked.connect(self._show_settings)
        
        # Recording controls
        self.record_button.clicked.connect(self._toggle_recording)
        
        # File operations
        self.file_list.file_selected.connect(self._on_file_selected)
        # self.file_list.itemDoubleClicked.connect(lambda item: self._start_transcription()) # Re-enable if needed
        self.transcribe_button.clicked.connect(self._start_transcription)
    
    def _switch_view(self, view_name):
        """Switch between recording and files view."""
        if view_name == "recording":
            self.content_stack.setCurrentIndex(0)
            self._update_nav_buttons(0)
            self.current_view = "recording"
        elif view_name == "files":
            self.content_stack.setCurrentIndex(1)
            self._update_nav_buttons(1)
            self.current_view = "files"
            self._refresh_audio_files()

    def _update_nav_buttons(self, active_index):
        """Update navigation button styles based on the active view."""
        self.record_nav_btn.set_style("primary" if active_index == 0 else "secondary")
        self.files_nav_btn.set_style("primary" if active_index == 1 else "secondary")
    
    
    def _show_settings(self):
        """Show settings dialog."""
        from .settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec():
            # Reload configuration if needed
            pass
    
    def _load_initial_data(self):
        """Load initial data."""
        self._populate_microphones()
        self._refresh_audio_files()
    
    def _populate_microphones(self):
        """Populate microphone selector."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            
            self.mic_selector.clear()
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.mic_selector.addItem(f"{device['name']}", i)
        except Exception as e:
            # Fallback if sounddevice not available
            self.mic_selector.clear()
            self.mic_selector.addItem("Default Microphone", 0)

    def _refresh_audio_files(self):
        """Refresh the audio files list."""
        try:
            self.file_list.clear_files()
            files = self.file_manager.get_audio_files()
            if files:
                self.files_container.setCurrentWidget(self.file_list)
                for file_info in files:
                    self.file_list.add_file(file_info)
            else:
                # Show message when no files
                self.files_container.setCurrentWidget(self.no_files_label)
        except Exception as e:
            print(f"Error refreshing files: {e}")
            # Show error message
            self.no_files_label.setText(f"Erro ao carregar arquivos: {str(e)}")
            self.no_files_label.setStyleSheet(f"color: {COLORS['danger']}; padding: 20px; border: 1px solid {COLORS['danger']}; border-radius: 8px;")
            self.files_container.setCurrentWidget(self.no_files_label)

    def _toggle_recording(self):
        """Toggle recording state."""
        if not self.audio_recorder.recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """Start recording."""
        selected_device_index = self.mic_selector.currentData()
        if selected_device_index is None:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Erro de Gravação", "Nenhum microfone selecionado ou disponível.")
            return

        if self.audio_recorder.start_recording(selected_device_index):
            # Update button appearance
            self.record_button.setText("")
            self.record_button.setIcon(qta.icon("fa5s.stop"))
            self.record_button.setStyleSheet(f"""
                ModernButton {{
                    border-radius: 40px;
                    font-size: 24px;
                    background-color: #ff4757;
                    border: 3px solid #ff4757;
                }}
                ModernButton:hover {{
                    background-color: #ff3742;
                    border-color: #ff3742;
                }}
            """)
            
            # Pass reference to audio recorder for real-time data
            self.waveform.audio_recorder = self.audio_recorder
            self.waveform.start_recording()
            
            # Start timer for recording duration
            self.recording_timer = QTimer()
            self.recording_timer.timeout.connect(self._update_recording_time)
            self.recording_timer.start(1000)
            self.recording_start_time = 0
    
    def _stop_recording(self):
        """Stop recording."""
        if self.audio_recorder.recording:
            audio_file = self.audio_recorder.stop_recording()
            if audio_file:
                # Update button appearance back to record
                self.record_button.setText("")
                self.record_button.setIcon(qta.icon("fa5s.microphone"))
                self.record_button.setStyleSheet(f"""
                    ModernButton {{
                        border-radius: 40px;
                        font-size: 24px;
                        background-color: {COLORS['accent']};
                        border: 3px solid {COLORS['accent']};
                    }}
                    ModernButton:hover {{
                        background-color: {COLORS['accent_hover']};
                        border-color: {COLORS['accent_hover']};
                    }}
                """)
                
                self.waveform.stop_recording()
                
                # Stop timer and reset display
                if hasattr(self, 'recording_timer') and self.recording_timer:
                    self.recording_timer.stop()
                    self.recording_timer.deleteLater()
                    self.recording_timer = None
                
                # Reset recording time display
                self.recording_status.setText("00:00:00")
                self.recording_start_time = 0
                
                print("DEBUG: Timer stopped and reset")
                
                # Visual feedback for successful recording
                self._show_recording_success_feedback()
                
                # Refresh file list
                self._refresh_audio_files()
                
                # Auto-select the new file
                for i in range(self.file_list.count()):
                    item = self.file_list.item(i)
                    if item.data(Qt.UserRole) == audio_file:
                        self.file_list.setCurrentItem(item)
                        break
    
    def _show_recording_success_feedback(self):
        """Show toast notification for successful recording."""
        print("DEBUG: Showing toast feedback")
        
        # Create toast notification widget
        toast = QWidget(self)
        toast.setFixedSize(300, 60)
        toast.setStyleSheet("""
            QWidget {
                background-color: #00F5D4;
                border: 2px solid #00E5C4;
                border-radius: 8px;
                color: #000000;
            }
        """)
        
        # Create layout and label for toast
        from PySide6.QtWidgets import QHBoxLayout, QLabel
        from PySide6.QtCore import Qt
        layout = QHBoxLayout(toast)
        
        # Success icon
        icon_label = QLabel("✓")
        icon_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
        
        # Success message
        message_label = QLabel("Gravação salva com sucesso!")
        message_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #000000;")
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Position toast at top-right of window
        parent_rect = self.rect()
        toast_x = parent_rect.width() - toast.width() - 20
        toast_y = 20
        toast.move(toast_x, toast_y)
        
        print(f"DEBUG: Toast positioned at {toast_x}, {toast_y}")
        
        # Show toast
        toast.show()
        toast.raise_()
        
        print("DEBUG: Toast shown and raised")
        
        # Auto-hide toast after 3 seconds
        hide_timer = QTimer()
        hide_timer.setSingleShot(True)
        hide_timer.timeout.connect(lambda: self._hide_toast(toast))
        hide_timer.start(3000)
        
        # Store timer reference to prevent garbage collection
        self.toast_timer = hide_timer
        
        # Temporary button color change
        self.record_button.setStyleSheet("""
            ModernButton {
                border-radius: 40px;
                font-size: 24px;
                background-color: #00F5D4;
                border: 3px solid #00F5D4;
            }
            ModernButton:hover {
                background-color: #00E5C4;
                border-color: #00E5C4;
            }
        """)
        
        # Reset button style after 1 second
        reset_timer = QTimer()
        reset_timer.setSingleShot(True)
        reset_timer.timeout.connect(self._reset_record_button_style)
        reset_timer.start(1000)
        self.button_reset_timer = reset_timer
    
    def _hide_toast(self, toast):
        """Hide and delete toast widget."""
        print("DEBUG: Hiding toast")
        if toast:
            toast.hide()
            toast.deleteLater()
    
    def _reset_record_button_style(self):
        """Reset record button to normal style after feedback."""
        self.record_button.setStyleSheet(f"""
            ModernButton {{
                border-radius: 40px;
                font-size: 24px;
                background-color: {COLORS['accent']};
                border: 3px solid {COLORS['accent']};
            }}
            ModernButton:hover {{
                background-color: {COLORS['accent_hover']};
                border-color: {COLORS['accent_hover']};
            }}
        """)
    
    def _update_recording_time(self):
        """Update recording time display."""
        self.recording_start_time += 1
        hours = self.recording_start_time // 3600
        minutes = (self.recording_start_time % 3600) // 60
        seconds = self.recording_start_time % 60
        self.recording_status.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def _on_file_selected(self, file_path):
        """Handle file selection."""
        self.current_audio_file = file_path
        self.transcribe_button.setEnabled(True)
    
    def _start_transcription(self):
        """Start transcription process."""
        if not self.current_audio_file:
            return
        
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QThread
        
        # Show custom modern progress dialog
        self.progress_dialog = ModernProgressDialog(self)
        self.progress_dialog.show()
        
        # Setup worker thread
        self.transcription_thread = QThread()
        import logging
        from pathlib import Path
        
        # Ensure we have absolute path
        if self.current_audio_file:
            abs_path = str(Path(self.current_audio_file).resolve())
            logging.info(f"[UI] Arquivo selecionado: {self.current_audio_file}")
            logging.info(f"[UI] Caminho absoluto: {abs_path}")
            logging.info(f"[UI] Arquivo existe: {Path(abs_path).exists()}")
        else:
            logging.error("[UI] Nenhum arquivo selecionado")
            return

        self.transcription_worker = TranscriptionWorker(self.transcription_engine, abs_path)
        self.transcription_worker.moveToThread(self.transcription_thread)

        # Connect signals
        self.transcription_thread.started.connect(self.transcription_worker.run)
        self.transcription_worker.transcription_completed.connect(self._on_transcription_completed)
        self.transcription_worker.transcription_failed.connect(self._on_transcription_failed)
        
        # Cleanup thread on completion
        self.transcription_worker.transcription_completed.connect(self.transcription_thread.quit)
        self.transcription_worker.transcription_failed.connect(self.transcription_thread.quit)
        self.transcription_thread.finished.connect(self.transcription_thread.deleteLater)
        self.transcription_worker.transcription_completed.connect(self.transcription_worker.deleteLater)
        self.transcription_worker.transcription_failed.connect(self.transcription_worker.deleteLater)
        
        # Connect progress dialog cancel
        self.progress_dialog.cancel_button.clicked.connect(self._cancel_transcription)
        
        # Disable transcribe button
        self.transcribe_button.setEnabled(False)
        
        # Start thread
        self.transcription_thread.start()
    
    def _on_transcription_completed(self, result):
        """Handle transcription completion."""
        import logging
        logging.info(f"Transcription completed. Full result received: {result}")
        self.progress_dialog.close()

        try:
            self.transcription_history.save_transcription(result)
        except Exception as e:
            logging.error(f"Failed to save transcription: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Salvar Falhou", f"Não foi possível salvar a transcrição:\n{e}")

        # Show result in dialog
        self._show_transcription_result(result)

        self.transcribe_button.setEnabled(True)
        
        
    
    def _on_transcription_failed(self, error):
        """Handle transcription failure."""
        print(f"Transcription failed. Error: {error}")
        self.progress_dialog.close()
        self.transcribe_button.setEnabled(True)
        
        if self.transcription_thread:
            self.transcription_thread.quit()
            self.transcription_thread.wait()
        
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Erro na Transcrição", f"Falha ao transcrever: {error}")
    
    def _cancel_transcription(self):
        """Cancel transcription."""
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            
        if hasattr(self, 'transcription_thread') and self.transcription_thread and self.transcription_thread.isRunning():
            self.transcription_thread.quit()
            self.transcription_thread.wait()
        
        self.transcribe_button.setEnabled(True)

    def _show_transcription_result(self, result):
        """Show transcription result in a dialog."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout

        dialog = QDialog(self)
        dialog.setWindowTitle("Transcrição Concluída")
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet(f"background-color: {COLORS['surface']}; color: {COLORS['text']};")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)

        text_edit = QTextEdit()
        text_edit.setPlainText(result.get('text', ''))
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
        """)
        layout.addWidget(text_edit)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addStretch()

        copy_button = ModernButton("Copiar Texto", "fa5s.copy", "secondary")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(result.get('text', '')))
        button_layout.addWidget(copy_button)

        close_button = ModernButton("Fechar", "fa5s.times", "primary")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        dialog.exec()

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)


