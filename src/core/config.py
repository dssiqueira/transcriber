"""
Configuration management system for the transcriber application.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class WhisperConfig:
    """Configuration for Whisper models."""
    selected_model: str = "base"
    language: str = "pt"
    temperature: float = 0.2
    best_of: int = 2
    initial_prompt: str = "Transcrição em português brasileiro:"


@dataclass
class AudioConfig:
    """Configuration for audio recording."""
    sample_rate: int = 44100
    channels: int = 1
    dtype: str = "float32"
    blocksize: int = 1024
    latency: str = "low"


@dataclass
class UIConfig:
    """Configuration for UI settings."""
    theme: str = "dark"
    window_width: int = 800
    window_height: int = 600
    auto_save_transcriptions: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""
    whisper: WhisperConfig
    audio: AudioConfig
    ui: UIConfig
    total_savings: float = 0.0

    def __post_init__(self):
        if isinstance(self.whisper, dict):
            self.whisper = WhisperConfig(**self.whisper)
        if isinstance(self.audio, dict):
            self.audio = AudioConfig(**self.audio)
        if isinstance(self.ui, dict):
            self.ui = UIConfig(**self.ui)


class ConfigManager:
    """Manages application configuration with file persistence."""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "app_config.json"
        self.legacy_whisper_file = self.config_dir / "whisper_settings.json"
        self.legacy_savings_file = self.config_dir / "savings.json"
        
        self._config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file, with legacy support."""
        config_data = {}
        
        # Try to load from new config file
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                pass  # Config file not found or invalid
        
        # Migrate from legacy files if they exist
        if not config_data:
            config_data = self._migrate_legacy_config()
        
        return AppConfig(
            whisper=WhisperConfig(**config_data.get('whisper', {})),
            audio=AudioConfig(**config_data.get('audio', {})),
            ui=UIConfig(**config_data.get('ui', {})),
            total_savings=config_data.get('total_savings', 0.0)
        )
    
    def _migrate_legacy_config(self) -> Dict[str, Any]:
        """Migrate configuration from legacy files."""
        config_data = {
            'whisper': {},
            'audio': {},
            'ui': {},
            'total_savings': 0.0
        }
        
        # Migrate whisper settings
        if self.legacy_whisper_file.exists():
            try:
                with open(self.legacy_whisper_file, 'r', encoding='utf-8') as f:
                    legacy_whisper = json.load(f)
                    config_data['whisper']['selected_model'] = legacy_whisper.get('selected_model', 'base')
            except (json.JSONDecodeError, IOError):
                pass
        
        # Migrate savings
        if self.legacy_savings_file.exists():
            try:
                with open(self.legacy_savings_file, 'r', encoding='utf-8') as f:
                    legacy_savings = json.load(f)
                    config_data['total_savings'] = legacy_savings.get('total_savings', 0.0)
            except (json.JSONDecodeError, IOError):
                pass
        
        return config_data
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self._config), f, indent=2, ensure_ascii=False)
        except IOError as e:
            pass  # Error saving config
    
    @property
    def config(self) -> AppConfig:
        """Get current configuration."""
        return self._config
    
    def update_whisper_model(self, model: str) -> None:
        """Update selected Whisper model."""
        self._config.whisper.selected_model = model
        self.save_config()
    
    def update_savings(self, amount: float) -> None:
        """Add to total savings."""
        self._config.total_savings += amount
        self.save_config()
    
    def get_whisper_models(self) -> Dict[str, Dict[str, Any]]:
        """Get available Whisper models information."""
        return {
            'tiny': {
                'name': 'Tiny',
                'size': '39MB',
                'description': 'Modelo mais rápido e leve, ideal para testes e transcrições simples.',
                'color': '#FF6B6B'
            },
            'small': {
                'name': 'Small',
                'size': '142MB',
                'description': 'Equilíbrio entre velocidade e precisão. Recomendado para a maioria dos casos.',
                'color': '#FF9F1C'
            },
            'base': {
                'name': 'Base',
                'size': '466MB',
                'description': 'Maior precisão que o Small, mantendo boa performance.',
                'color': '#FFD93D'
            },
            'medium': {
                'name': 'Medium',
                'size': '1.5GB',
                'description': 'Alta precisão e excelente reconhecimento de contexto.',
                'color': '#4CAF50'
            },
            'large': {
                'name': 'Large',
                'size': '2.9GB',
                'description': 'Máxima precisão e melhor compreensão de contexto.',
                'color': '#2196F3'
            }
        }
