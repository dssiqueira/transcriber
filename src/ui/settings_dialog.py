"""
Settings dialog showing savings and model selection.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QGroupBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import qtawesome as qta

from .styles import COLORS


class SettingsDialog(QDialog):
    """Settings dialog with savings display and model selection."""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Title
        title_label = QLabel("Settings")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {COLORS['text']};")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Savings section
        savings_group = self.create_savings_section()
        layout.addWidget(savings_group)
        
        # Model selection section
        model_group = self.create_model_section()
        layout.addWidget(model_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_button = QPushButton("Save Changes")
        save_button.setFixedHeight(40)
        save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: #ff6b7a;
            }}
        """)
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedHeight(40)
        cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                font-size: 14px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['hover']};
            }}
        """)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addLayout(button_layout)
        
        # Apply dark theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                font-family: "Segoe UI", sans-serif;
            }}
        """)
    
    def create_savings_section(self):
        """Create the savings display section."""
        group = QGroupBox("Your Savings")
        group.setFont(QFont("Segoe UI", 14, QFont.Bold))
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Calculate savings based on actual duration
        total_transcriptions = self.get_total_transcriptions()
        total_duration_minutes = self.get_total_duration_minutes()
        estimated_savings = self.calculate_savings(total_transcriptions)
        
        # Savings display
        savings_frame = QFrame()
        savings_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        savings_layout = QVBoxLayout(savings_frame)
        
        # Total saved
        total_label = QLabel(f"R$ {estimated_savings:.2f}")
        total_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        total_label.setStyleSheet(f"color: {COLORS['accent']};")
        total_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Total economizado em transcrições")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet(f"color: {COLORS['secondary_text']};")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Stats
        stats_layout = QHBoxLayout()
        
        transcriptions_stat = self.create_stat_widget("Transcrições", str(total_transcriptions))
        duration_stat = self.create_stat_widget("Total (min)", f"{total_duration_minutes:.1f}")
        cost_per_stat = self.create_stat_widget("Custo/min", "R$ 0,033")
        
        stats_layout.addWidget(transcriptions_stat)
        stats_layout.addWidget(duration_stat)
        stats_layout.addWidget(cost_per_stat)
        
        savings_layout.addWidget(total_label)
        savings_layout.addWidget(subtitle_label)
        savings_layout.addSpacing(10)
        savings_layout.addLayout(stats_layout)
        
        layout.addWidget(savings_frame)
        
        return group
    
    def create_model_section(self):
        """Create the model selection section."""
        group = QGroupBox("Whisper Model")
        group.setFont(QFont("Segoe UI", 14, QFont.Bold))
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }}
        """)
        
        layout = QFormLayout(group)
        layout.setSpacing(15)
        
        # Model selection
        model_label = QLabel("Modelo:")
        model_label.setStyleSheet(f"color: {COLORS['text']};")
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "tiny - Fastest, lower accuracy (Recommended)",
            "base - Balanced speed/accuracy", 
            "small - Better accuracy, slower",
            "medium - High accuracy, slow",
            "large - Best accuracy, very slow"
        ])
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 20px;
            }}
            QComboBox:hover {{
                border-color: {COLORS['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        
        layout.addRow(model_label, self.model_combo)
        
        # Model info
        info_label = QLabel("Modelos maiores oferecem melhor precisão mas são mais lentos.")
        info_label.setStyleSheet(f"color: {COLORS['secondary_text']}; font-size: 11px;")
        info_label.setWordWrap(True)
        layout.addRow("", info_label)
        
        return group
    
    def create_stat_widget(self, title, value):
        """Create a stat display widget."""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 6px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['text']};")
        value_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 10))
        title_label.setStyleSheet(f"color: {COLORS['secondary_text']};")
        title_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(title_label)
        
        return widget
    
    def get_total_transcriptions(self):
        """Get total number of transcriptions."""
        try:
            import json
            import os
            history_file = os.path.join("transcriptions", "transcription_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return len(history)
            return 0
        except:
            return 0
    
    def get_total_duration_minutes(self):
        """Get total duration of all transcriptions in minutes."""
        try:
            import json
            import os
            history_file = os.path.join("transcriptions", "transcription_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                total_seconds = sum(item.get('duration', 0) for item in history)
                return total_seconds / 60.0  # Convert to minutes
            return 0.0
        except:
            return 0.0
    
    def calculate_savings(self, transcriptions):
        """Calculate estimated savings based on actual audio duration."""
        # Get total duration from transcription history
        total_duration_minutes = self.get_total_duration_minutes()
        
        # OpenAI Whisper API: $0.006 per minute
        # Convert to BRL (approximate rate: 1 USD = 5.5 BRL)
        usd_per_minute = 0.006
        brl_per_minute = usd_per_minute * 5.5  # R$ 0.033 per minute
        
        return total_duration_minutes * brl_per_minute
    
    def load_settings(self):
        """Load current settings."""
        try:
            whisper_config = self.config_manager.get_whisper_settings()
            model_name = whisper_config.get('model', 'base')
            
            # Map model name to combo box index
            model_map = {
                'tiny': 0,
                'base': 1,
                'small': 2,
                'medium': 3,
                'large': 4
            }
            
            if model_name in model_map:
                self.model_combo.setCurrentIndex(model_map[model_name])
        except:
            # Default to base model
            self.model_combo.setCurrentIndex(1)
    
    def save_settings(self):
        """Save settings changes."""
        try:
            # Get selected model
            model_index = self.model_combo.currentIndex()
            model_names = ['tiny', 'base', 'small', 'medium', 'large']
            selected_model = model_names[model_index]
            
            # Update whisper settings
            whisper_config = self.config_manager.get_whisper_settings()
            whisper_config['model'] = selected_model
            self.config_manager.update_whisper_settings(whisper_config)
            
            self.accept()
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Failed to save settings: {str(e)}")
