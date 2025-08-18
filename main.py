#!/usr/bin/env python3
"""
Audio Transcriber - Main entry point
"""
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """Main application entry point."""
    try:
        # Setup logging
        from src.utils.logging import initialize_app_logging
        from src.core.config import ConfigManager
        config_manager = ConfigManager()
        initialize_app_logging(str(config_manager.config_dir))
        
        # Create QApplication
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QIcon
        
        app = QApplication(sys.argv)
        app.setApplicationName("Audio Transcriber")
        app.setApplicationVersion("2.0")
        
        # Set application icon
        icon_path = Path(__file__).parent / "img" / "voice.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Create main window
        from src.ui.modern_window import ModernTranscriberWindow
        window = ModernTranscriberWindow()
        
        # Show window
        window.show()
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
