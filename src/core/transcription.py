"""
Transcription engine with async processing and multiple provider support.
"""
import asyncio
import threading
from typing import Dict, Any, Optional, Callable, Protocol
from pathlib import Path
from datetime import datetime
import json
import logging


class TranscriptionProvider(Protocol):
    """Protocol for transcription providers."""
    
    def transcribe(self, audio_file: str, **kwargs) -> Dict[str, Any]:
        """Transcribe audio file and return result."""
        ...
    
    def get_name(self) -> str:
        """Get provider name."""
        ...


class WhisperProvider:
    """Local Whisper transcription provider."""
    
    def __init__(self, model_name: str = "tiny"):
        self.model_name = model_name
        self._model = None
    
    def _load_model(self):
        """Lazy load Whisper model with optimizations."""
        if self._model is None:
            import whisper
            import torch
            
            # Use GPU if available for faster processing
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            self._model = whisper.load_model(
                self.model_name, 
                device=device,
                download_root=None,  # Use default cache
                in_memory=True  # Keep model in memory
            )
            
            # Enable optimizations
            if device == "cuda":
                self._model = self._model.half()  # Use half precision on GPU
                
        return self._model
    
    def transcribe(self, audio_file: str, **kwargs) -> Dict[str, Any]:
        """Transcribe audio using Whisper by passing the file path directly."""
        try:
            audio_path = Path(audio_file)
            logging.info(f"[WhisperProvider] Caminho recebido: {audio_file}")
            logging.info(f"[WhisperProvider] Caminho absoluto: {audio_path.resolve()}")
            logging.info(f"[WhisperProvider] Arquivo existe: {audio_path.exists()}")
            
            if not audio_path.exists():
                raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")
            
            if audio_path.stat().st_size == 0:
                raise FileNotFoundError(f"Arquivo de áudio vazio: {audio_file}")

            model = self._load_model()
            import torch

            # Configuration for better accuracy with Portuguese language
            config = {
                'task': 'transcribe',
                'language': 'pt',  # Force Portuguese
                'temperature': 0.0,
                'best_of': 5,
                'beam_size': 5,
                'patience': 1.0,
                'length_penalty': 1.0,
                'suppress_tokens': [-1],
                'initial_prompt': "Transcrição em português brasileiro.",
                'fp16': torch.cuda.is_available(),
                **kwargs
            }

            logging.info("Forçando idioma português para evitar detecção incorreta.")

            # Use absolute path for Whisper with Windows path normalization
            absolute_path = str(audio_path.resolve())
            # Normalize path for Windows
            normalized_path = absolute_path.replace('\\', '/')
            logging.info(f"[WhisperProvider] Passando para Whisper: {normalized_path}")
            
            # Try to load audio first to verify it's accessible
            try:
                import soundfile as sf
                import numpy as np
                audio_data, sample_rate = sf.read(absolute_path)
                logging.info(f"[WhisperProvider] Áudio carregado com sucesso: {len(audio_data)} samples, {sample_rate} Hz")
                
                # Convert to float32 to ensure compatibility with Whisper
                audio_data = audio_data.astype(np.float32)
                
                # Ensure mono audio (Whisper expects mono)
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                # Normalize audio to prevent clipping and improve quality
                if np.max(np.abs(audio_data)) > 0:
                    audio_data = audio_data / np.max(np.abs(audio_data)) * 0.95
                
                # Resample to 16kHz if needed (Whisper's expected sample rate)
                if sample_rate != 16000:
                    try:
                        import librosa
                        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
                        sample_rate = 16000
                        logging.info(f"[WhisperProvider] Áudio reamostrado para 16kHz")
                    except ImportError:
                        logging.warning(f"[WhisperProvider] librosa não disponível, mantendo sample rate {sample_rate}Hz")
                        # Continue without resampling - Whisper can handle different sample rates
                
                logging.info(f"[WhisperProvider] Áudio processado: dtype={audio_data.dtype}, shape={audio_data.shape}, sample_rate={sample_rate}")
                
                # Pass the audio data directly to Whisper instead of file path
                raw_result = model.transcribe(audio_data, **config)
            except Exception as e:
                logging.error(f"[WhisperProvider] Erro ao carregar áudio: {e}")
                raise FileNotFoundError(f"Não foi possível carregar o arquivo de áudio: {e}")
            logging.info(f"Whisper raw result: {raw_result}")

            return {
                'text': raw_result.get('text', '').strip(),
                'language': raw_result.get('language', 'unknown'),
                'segments': raw_result.get('segments', []),
                'provider': self.get_name(),
                'model': self.model_name,
                'success': True
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logging.error(f"Falha na transcrição: {e}\n{error_details}")
            return {
                'text': '',
                'error': f'Erro na transcrição: {str(e)}',
                'error_details': error_details,
                'provider': self.get_name(),
                'model': self.model_name,
                'success': False
            }
    
    def get_name(self) -> str:
        return "Whisper Local"


class TranscriptionEngine:
    """Main transcription engine with async processing."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.providers = {}
        self.current_task = None
        self._setup_providers()
    
    def _setup_providers(self):
        """Initialize transcription providers."""
        # Setup Whisper provider
        model = self.config_manager.config.whisper.selected_model
        self.providers['whisper'] = WhisperProvider(model)
    
    def get_available_providers(self) -> Dict[str, str]:
        """Get list of available transcription providers."""
        return {key: provider.get_name() for key, provider in self.providers.items()}
    
    async def transcribe_async(
        self,
        audio_file: str,
        provider: str = 'whisper',
        progress_callback: Optional[Callable[[int, str], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Transcribe audio file asynchronously."""
        if provider not in self.providers:
            return {
                'success': False,
                'error': f'Provider {provider} not available'
            }
        
        if progress_callback:
            progress_callback(10, "Preparando transcrição...")
        
        # Get file info for cost calculation
        try:
            import soundfile as sf
            info = sf.info(audio_file)
            duration = info.duration
        except Exception:
            duration = 0
        
        if progress_callback:
            progress_callback(20, "Carregando modelo...")
        
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        provider_instance = self.providers[provider]
        
        try:
            if progress_callback:
                progress_callback(40, "Transcrevendo áudio...")
            
            result = await loop.run_in_executor(
                None,
                provider_instance.transcribe,
                audio_file,
                **kwargs
            )
            
            if progress_callback:
                progress_callback(80, "Finalizando...")
            
            # Add metadata
            result.update({
                'audio_file': audio_file,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'estimated_cost': self._calculate_cost(duration)
            })
            
            # Update savings if successful
            if result.get('success', False):
                self.config_manager.update_savings(result['estimated_cost'])
            
            if progress_callback:
                progress_callback(100, "Concluído!")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'audio_file': audio_file,
                'provider': provider_instance.get_name()
            }
    
    def transcribe_sync(
        self,
        audio_file: str,
        provider: str = 'whisper',
        progress_callback: Optional[Callable[[int, str], None]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Synchronous wrapper for transcription that runs in a separate thread."""
        if provider not in self.providers:
            return {'success': False, 'error': f'Provider {provider} not available'}

        provider_instance = self.providers[provider]
        if progress_callback: progress_callback(10, "Iniciando transcrição...")

        try:
            if progress_callback: progress_callback(40, "Transcrevendo áudio...")
            transcription_result = provider_instance.transcribe(audio_file, **kwargs)
            if progress_callback: progress_callback(80, "Finalizando...")

            if not transcription_result.get('success', False):
                return transcription_result

            # Add metadata
            try:
                import soundfile as sf
                info = sf.info(audio_file)
                duration = info.duration
            except Exception:
                duration = 0

            transcription_result.update({
                'audio_file': audio_file,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'estimated_cost': self._calculate_cost(duration)
            })

            if transcription_result.get('success', False):
                self.config_manager.update_savings(transcription_result['estimated_cost'])

            if progress_callback: progress_callback(100, "Concluído!")
            logging.info(f"Transcription engine result: {transcription_result}")
            return transcription_result

        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': str(e),
                'error_details': traceback.format_exc(),
                'audio_file': audio_file,
                'provider': provider_instance.get_name()
            }
    
    def _calculate_cost(self, duration_seconds: float) -> float:
        """Calculate estimated transcription cost."""
        return (duration_seconds / 60) * 0.006
    
    def cancel_current_task(self):
        """Cancel current transcription task."""
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()


class TranscriptionHistory:
    """Manages transcription history and caching."""
    
    def __init__(self, history_dir: str):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.history_file = self.history_dir / "transcription_history.json"
    
    def save_transcription(self, result: Dict[str, Any]) -> str:
        """Save transcription result to history."""
        try:
            # Generate unique ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_name = Path(result.get('audio_file', 'unknown')).stem
            transcription_id = f"{audio_name}_{timestamp}"
            
            # Save full result
            result_file = self.history_dir / f"{transcription_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Update history index
            self._update_history_index(transcription_id, result)
            
            return transcription_id
            
        except Exception as e:
            pass  # Error handled
            return ""
    
    def _update_history_index(self, transcription_id: str, result: Dict[str, Any]):
        """Update the history index file."""
        try:
            # Load existing history
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Add new entry
            history.append({
                'id': transcription_id,
                'audio_file': result.get('audio_file', ''),
                'duration': result.get('duration', 0),
                'provider': result.get('provider', ''),
                'model': result.get('model', ''),
                'timestamp': result.get('timestamp', ''),
                'success': result.get('success', False),
                'text_preview': result.get('text', '')[:100] + '...' if len(result.get('text', '')) > 100 else result.get('text', '')
            })
            
            # Keep only last 100 entries
            history = history[-100:]
            
            # Save updated history
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            pass  # Error handled
    
    def get_history(self) -> list:
        """Get transcription history."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            pass  # Error handled
        
        return []
    
    def get_transcription(self, transcription_id: str) -> Optional[Dict[str, Any]]:
        """Get full transcription result by ID."""
        try:
            result_file = self.history_dir / f"{transcription_id}.json"
            if result_file.exists():
                with open(result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            pass  # Error handled
        
        return None
    
    def delete_transcription(self, transcription_id: str) -> bool:
        """Delete a transcription from history."""
        try:
            # Remove result file
            result_file = self.history_dir / f"{transcription_id}.json"
            if result_file.exists():
                result_file.unlink()
            
            # Update history index
            history = self.get_history()
            history = [entry for entry in history if entry['id'] != transcription_id]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            pass  # Error handled
            return False
