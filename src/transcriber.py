"""
Whisper transcription module.
Optimized for M2 MacBook Air performance.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()

class WhisperTranscriber:
    """Handles audio transcription using Whisper."""
    
    def __init__(self, model_size: str = "small", device: str = "auto", compute_type: str = "float16"):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (auto, cpu, cuda, mps)
            compute_type: Compute type (float16, float32, int8)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        console.print(f"[blue]Loading Whisper model: {model_size}[/blue]")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        console.print(f"[green]✅ Whisper model loaded successfully![/green]")
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional, auto-detect if None)
            
        Returns:
            Dictionary containing transcription data
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        console.print(f"[blue]Starting transcription of: {Path(audio_path).name}[/blue]")
        
        # Get audio duration for progress tracking
        audio_duration = self._get_audio_duration(audio_path)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Transcribing...", total=audio_duration)
            
            try:
                # Transcribe with progress updates
                segments, info = self.model.transcribe(
                    audio_path,
                    language=language,
                    beam_size=5,
                    word_timestamps=True
                )
                
                # Process segments
                full_text = ""
                segments_list = []
                
                for segment in segments:
                    full_text += segment.text + " "
                    segments_list.append({
                        'start': segment.start,
                        'end': segment.end,
                        'text': segment.text,
                        'words': segment.words if hasattr(segment, 'words') else []
                    })
                    
                    # Update progress
                    progress.update(task, completed=segment.end)
                
                progress.update(task, description="✅ Transcription completed!")
                
                return {
                    'text': full_text.strip(),
                    'segments': segments_list,
                    'language': info.language,
                    'language_probability': info.language_probability,
                    'duration': audio_duration
                }
                
            except Exception as e:
                progress.update(task, description=f"❌ Transcription failed: {e}")
                raise
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            import ffmpeg
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['streams'][0]['duration'])
            return duration
        except Exception:
            # Fallback: estimate based on file size
            file_size = os.path.getsize(audio_path)
            # Rough estimate: 1MB ≈ 1 minute of audio
            return file_size / (1024 * 1024) * 60
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'model_name': f"whisper-{self.model_size}"
        }
    
    def estimate_transcription_time(self, audio_duration: float) -> float:
        """
        Estimate transcription time based on audio duration.
        Optimized for M2 MacBook Air performance.
        """
        # Rough estimates based on M2 performance
        if self.model_size == "tiny":
            return audio_duration * 0.1
        elif self.model_size == "base":
            return audio_duration * 0.15
        elif self.model_size == "small":
            return audio_duration * 0.2
        elif self.model_size == "medium":
            return audio_duration * 0.4
        elif self.model_size == "large":
            return audio_duration * 0.8
        else:
            return audio_duration * 0.3
