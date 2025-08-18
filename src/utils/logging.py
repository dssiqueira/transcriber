"""
Logging utilities for the transcriber application.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Setup application logging with both file and console handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        console_output: Whether to output to console
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('transcriber')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = ColoredFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f'transcriber.{name}')


class LogCapture:
    """Context manager for capturing log messages during testing or debugging."""
    
    def __init__(self, logger_name: str = 'transcriber', level: str = 'DEBUG'):
        self.logger_name = logger_name
        self.level = getattr(logging, level.upper())
        self.handler = None
        self.records = []
    
    def __enter__(self):
        # Create memory handler
        self.handler = logging.Handler()
        self.handler.setLevel(self.level)
        self.handler.emit = self._capture_record
        
        # Add to logger
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def _capture_record(self, record):
        """Capture log record."""
        self.records.append(record)
    
    def get_messages(self, level: Optional[str] = None) -> list:
        """Get captured messages, optionally filtered by level."""
        if level:
            target_level = getattr(logging, level.upper())
            return [r.getMessage() for r in self.records if r.levelno >= target_level]
        return [r.getMessage() for r in self.records]


# Application-wide logger setup
def initialize_app_logging(config_dir: str):
    """Initialize logging for the entire application."""
    log_dir = Path(config_dir) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"transcriber_{timestamp}.log"
    
    # Setup main logger
    logger = setup_logging(
        log_level="INFO",
        log_file=str(log_file),
        console_output=True
    )
    
    # Log startup
    logger.info("Transcriber application starting...")
    logger.info(f"Log file: {log_file}")
    
    return logger
