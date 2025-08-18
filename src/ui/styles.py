"""
UI styles and theming for the transcriber application.
"""

# Dark theme color palette
COLORS = {
    'primary': '#1a1a1a',
    'secondary': '#2d2d2d',
    'accent': '#ff4757',
    'accent_hover': '#ff3742',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#ff4757',
    'surface': '#2d2d2d',
    'background': '#1a1a1a',
    'text': '#ffffff',
    'primary_text': '#ffffff',
    'secondary_text': '#999999',
    'border': '#404040',
    'hover': '#333333',
    'card': '#2d2d2d',
    'input': '#2d2d2d',
    'waveform': '#00ff88'
}

# Main application stylesheet
MAIN_STYLE = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QWidget {{
    background-color: {COLORS['background']};
    color: {COLORS['primary_text']};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

/* Tab Widget */
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    background: {COLORS['background']};
    border-radius: 4px;
}}

QTabWidget::tab-bar {{
    alignment: left;
}}

QTabBar::tab {{
    background: {COLORS['surface']};
    color: {COLORS['secondary_text']};
    padding: 12px 16px;
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    min-width: 100px;
    font-size: 14px;
}}

QTabBar::tab:hover {{
    background: {COLORS['hover']};
    color: {COLORS['primary_text']};
}}

QTabBar::tab:selected {{
    background: {COLORS['hover']};
    color: {COLORS['primary_text']};
    border-bottom: none;
    font-weight: 500;
}}

QTabBar::tab:!selected {{
    margin-top: 2px;
}}

/* Labels */
QLabel {{
    color: {COLORS['primary_text']};
}}

/* Buttons */
QPushButton {{
    background-color: {COLORS['secondary']};
    color: {COLORS['primary_text']};
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: {COLORS['hover']};
}}

QPushButton:pressed {{
    background-color: {COLORS['surface']};
}}

QPushButton:disabled {{
    background-color: {COLORS['surface']};
    color: {COLORS['secondary_text']};
}}

/* Progress Bar */
QProgressBar {{
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    text-align: center;
    color: {COLORS['primary_text']};
    background-color: {COLORS['surface']};
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent']};
    border-radius: 3px;
}}

/* ComboBox */
QComboBox {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary_text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 5px 10px;
}}

QComboBox:hover {{
    border-color: {COLORS['hover']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid {COLORS['secondary_text']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['secondary']};
    color: {COLORS['primary_text']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['accent']};
}}

/* List Widget */
QListWidget {{
    background-color: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    color: {COLORS['primary_text']};
    padding: 5px;
}}

QListWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS['border']};
    border-radius: 3px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['accent']};
    color: {COLORS['primary_text']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['hover']};
}}

/* Text Edit */
QLineEdit, QTextEdit {{
    background-color: {COLORS['surface']};
    color: {COLORS['primary_text']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 5px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLORS['accent']};
}}

/* Radio Button */
QRadioButton {{
    color: {COLORS['primary_text']};
}}

QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {COLORS['border']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['accent']};
    border: 2px solid {COLORS['accent']};
}}

QRadioButton::indicator:unchecked:hover {{
    border: 2px solid {COLORS['accent']};
}}

/* Scroll Bar */
QScrollBar:vertical {{
    background: {COLORS['surface']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border']};
    border-radius: 6px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['accent']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    border: none;
    background: none;
}}

/* Frame */
QFrame {{
    border-radius: 4px;
}}

QFrame[frameShape="4"] {{ /* HLine */
    background-color: {COLORS['border']};
    max-height: 1px;
}}
"""

# Specialized button styles
BUTTON_STYLES = {
    'primary': f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #00b8a3;
        }}
        QPushButton:pressed {{
            background-color: #009688;
        }}
    """,
    
    'danger': f"""
        QPushButton {{
            background-color: {COLORS['danger']};
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #ff2b56;
        }}
        QPushButton:pressed {{
            background-color: #e6204a;
        }}
    """,
    
    'success': f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #45a049;
        }}
        QPushButton:pressed {{
            background-color: #3d8b40;
        }}
    """,
    
    'warning': f"""
        QPushButton {{
            background-color: {COLORS['warning']};
            color: #363636;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: #ffd83d;
        }}
        QPushButton:pressed {{
            background-color: #ffcd23;
        }}
    """
}

# Card/Container styles
CONTAINER_STYLES = {
    'card': f"""
        QWidget {{
            background-color: {COLORS['card']};
            border-radius: 8px;
            padding: 16px;
            margin: 8px;
        }}
    """,
    
    'info_panel': f"""
        QWidget {{
            background-color: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            padding: 12px;
            margin: 4px;
        }}
    """,
    
    'status_bar': f"""
        QLabel {{
            background-color: {COLORS['secondary']};
            color: {COLORS['accent']};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }}
    """
}

def get_model_radio_style(color: str) -> str:
    """Get radio button style for model selection with custom color."""
    return f"""
        QRadioButton {{
            font-weight: bold;
            color: {color};
            padding: 4px;
        }}
        QRadioButton::indicator {{
            width: 13px;
            height: 13px;
            border-radius: 7px;
            border: 2px solid {color};
        }}
        QRadioButton::indicator:checked {{
            background-color: {color};
            border: 2px solid {color};
        }}
        QRadioButton::indicator:unchecked:hover {{
            border: 2px solid {color};
            background-color: rgba({color[1:]}, 0.1);
        }}
    """

def get_vu_meter_style() -> str:
    """Get VU meter specific styling."""
    return f"""
        QFrame {{
            background-color: {COLORS['surface']};
            border: 2px solid {COLORS['border']};
            border-radius: 6px;
            margin: 8px;
        }}
    """
