"""
Audio processing utilities for the transcriber application.
"""
import os
import logging
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class AudioDevice:
    """Represents an audio input device."""
    index: int
    name: str
    channels: int
    samplerate: float
    is_default: bool = False


class AudioRecorder:
    """Handles audio recording functionality."""
    
    def __init__(self, audio_dir: str, config: Dict[str, Any]):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        
        self.config = config
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.current_sample_rate = config.get('sample_rate', 44100)
        
        # Callback for real-time audio level updates
        self.level_callback: Optional[Callable[[float], None]] = None
    
    def get_input_devices(self) -> List[AudioDevice]:
        """Get list of available input devices."""
        devices = []
        seen_names = set()
        
        try:
            device_list = sd.query_devices()
            default_device = sd.query_devices(kind='input')
            
            for i, device in enumerate(device_list):
                if device['name'] in seen_names or device['max_input_channels'] <= 0:
                    continue
                
                seen_names.add(device['name'])
                samplerate = device.get('default_samplerate', 44100)
                
                device_info = AudioDevice(
                    index=i,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    samplerate=samplerate,
                    is_default=(i == default_device['index'] if default_device else False)
                )
                
                if self._test_device(device_info):
                    devices.append(device_info)
                    
        except Exception as e:
            logging.error(f"Erro ao listar dispositivos de áudio: {e}", exc_info=True)
            pass  # Error listing devices
        
        return devices
    
    def _test_device(self, device: AudioDevice) -> bool:
        """Test if an audio device is available."""
        try:
            sd.query_devices(device.index)
            return True
        except Exception:
            return False
    
    def start_recording(self, device_index: int) -> bool:
        """Start audio recording."""
        try:
            if self.recording:
                return False
            
            # Get device info directly using the provided index
            device_info = sd.query_devices(device_index)
            if not device_info or device_info.get('max_input_channels', 0) == 0:
                raise Exception(f"Dispositivo inválido ou sem canais de entrada: {device_index}")

            device = AudioDevice(
                index=device_index,
                name=device_info['name'],
                channels=device_info['max_input_channels'],
                samplerate=device_info.get('default_samplerate', 44100)
            )
            
            # Audio configuration
            sample_rate = int(device.samplerate)
            channels = min(self.config.get('channels', 1), device.channels)
            dtype = self.config.get('dtype', 'float32')
            blocksize = self.config.get('blocksize', 1024)
            latency = self.config.get('latency', 'low')
            
            self.audio_data = []
            self.current_sample_rate = sample_rate
            
            def audio_callback(indata, frames, time, status):
                """This is called (from a separate thread) for each audio block."""
                if status:
                    logging.warning(f"Status da gravação: {status}")
                self.audio_data.append(indata.copy())

            self.stream = sd.InputStream(
                samplerate=sample_rate,
                device=device.index,
                channels=channels,
                dtype=dtype,
                blocksize=blocksize,
                latency=latency,
                callback=audio_callback
            )
            
            self.stream.start()
            self.recording = True
            return True
            
        except Exception as e:
            logging.error(f"Erro ao iniciar a gravação: {e}", exc_info=True)
            pass  # Error starting recording
            self.recording = False
            return False
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and save audio file."""
        if not self.recording or not self.stream:
            return None
        
        try:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.recording = False
            
            if not self.audio_data:
                return None
            
            # Process audio data
            audio_data = np.concatenate(self.audio_data, axis=0)
            
            # Normalize if needed
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.audio_dir.resolve() / f"gravacao_{timestamp}.wav"
            
            # Save file
            sf.write(str(filename), audio_data, self.current_sample_rate, 'PCM_16')
            
            return str(filename)
            
        except Exception as e:
            logging.error(f"Erro ao parar a gravação: {e}", exc_info=True)
            pass  # Error stopping recording
            self.recording = False
            return None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for processing audio data."""
        if status:
            pass  # Audio callback status
        
        self.audio_data.append(indata.copy())
        
        # Calculate RMS for level meter
        if self.level_callback and len(indata) > 0:
            rms = np.sqrt(np.mean(indata**2))
            self.level_callback(float(rms))
    
    def set_level_callback(self, callback: Callable[[float], None]):
        """Set callback for real-time audio level updates."""
        self.level_callback = callback
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording


class AudioFileManager:
    """Manages audio files and metadata."""
    
    def __init__(self, audio_dir: str):
        self.audio_dir = Path(audio_dir)
        self.audio_dir.mkdir(exist_ok=True)
        self.supported_formats = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    
    def get_audio_files(self) -> List[Dict[str, Any]]:
        """Get list of audio files with metadata."""
        files = []
        
        if not self.audio_dir.exists():
            return files
        
        for file_path in self.audio_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    # Try to get basic file info first
                    stat = file_path.stat()
                    
                    # Try to get audio info with soundfile
                    try:
                        info = sf.info(str(file_path))
                        duration = info.duration
                        samplerate = info.samplerate
                        channels = info.channels
                    except:
                        # If soundfile fails, use basic info
                        duration = 0.0
                        samplerate = 44100
                        channels = 1
                    
                    files.append({
                        'path': str(file_path.resolve()),
                        'name': file_path.name,
                        'duration': duration,
                        'samplerate': samplerate,
                        'channels': channels,
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
                except Exception as e:
                    # Skip files that can't be read at all
                    continue
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files
    
    def import_file(self, source_path: str) -> Optional[str]:
        """Import an audio file to the audio directory."""
        try:
            source = Path(source_path)
            if not source.exists():
                return None
            
            # Check if file is already in audio directory
            dest_path = self.audio_dir / source.name
            if dest_path.exists():
                # Generate unique name
                stem = source.stem
                suffix = source.suffix
                counter = 1
                while dest_path.exists():
                    dest_path = self.audio_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            # Copy file
            import shutil
            shutil.copy2(source_path, dest_path)
            return str(dest_path)
            
        except Exception as e:
            pass  # Error importing file
            return None
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an audio file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            info = sf.info(file_path)
            stat = path.stat()
            
            return {
                'path': file_path,
                'name': path.name,
                'duration': info.duration,
                'samplerate': info.samplerate,
                'channels': info.channels,
                'frames': info.frames,
                'format': info.format,
                'subtype': info.subtype,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
            
        except Exception as e:
            pass  # Error getting file info
            return None


def calculate_transcription_cost(duration_seconds: float, cost_per_minute: float = 0.006) -> float:
    """Calculate estimated transcription cost based on duration."""
    return (duration_seconds / 60) * cost_per_minute


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
