"""
Transcription processor that handles VideoDownloadedEvent and emits TranscriptGeneratedEvent.
"""

import time
from pathlib import Path
from rich.console import Console

from src.events.handlers.event_handler import EventProcessor
from src.events import VideoDownloadedEvent, TranscriptGeneratedEvent, TranscriptProcessingErrorEvent
from src.config import Config
from src.transcriber import WhisperTranscriber
from src.downloader import YouTubeDownloader

console = Console()


class TranscriptionProcessor(EventProcessor):
    """Processor that transcribes videos when VideoDownloadedEvent is received."""
    
    def __init__(self, event_bus, whisper_model: str = "small", transcription_method: str = "whisper"):
        super().__init__(event_bus, "TranscriptionProcessor")
        self.whisper_model = whisper_model
        self.transcription_method = transcription_method
        self.transcriber = WhisperTranscriber(
            model_size=whisper_model,
            device=Config.WHISPER_DEVICE,
            compute_type=Config.WHISPER_COMPUTE_TYPE
        )
        self.downloader = YouTubeDownloader(Config.TEMP_DIR)
    
    def handle(self, event: VideoDownloadedEvent):
        """
        Handle VideoDownloadedEvent by transcribing the audio.
        
        Args:
            event: VideoDownloadedEvent containing audio path and video info
        """
        console.print(f"[blue]🎤 Transcribing video: {event.video_info.title}[/blue]")
        
        start_time = time.time()
        
        try:
            if self.transcription_method == "captions":
                # Try to download captions
                transcript_result = self._transcribe_with_captions(event)
            else:
                # Use Whisper transcription
                transcript_result = self._transcribe_with_whisper(event)
            
            processing_duration = time.time() - start_time
            
            # Emit TranscriptGeneratedEvent
            transcript_event = TranscriptGeneratedEvent(
                video_id=event.video_id,
                transcript_text=transcript_result['text'],
                language=transcript_result.get('language', 'en'),
                language_probability=transcript_result.get('language_probability', 0.0),
                segments=transcript_result.get('segments', []),
                transcription_method=self.transcription_method,
                processing_duration=processing_duration,
                source=self.name
            )
            
            self.publish_event(transcript_event)
            return transcript_result
            
        except Exception as e:
            # Emit error event
            error_event = TranscriptProcessingErrorEvent(
                video_id=event.video_id,
                error_message=str(e),
                error_type=type(e).__name__,
                transcription_method=self.transcription_method,
                source=self.name
            )
            self.publish_event(error_event)
            raise
    
    def _transcribe_with_whisper(self, event: VideoDownloadedEvent) -> dict:
        """Transcribe using Whisper."""
        return self.transcriber.transcribe(event.audio_path)
    
    def _transcribe_with_captions(self, event: VideoDownloadedEvent) -> dict:
        """Transcribe using YouTube captions."""
        # Try to download captions using the original URL
        captions_path = self.downloader.download_captions(event.url)
        
        if not captions_path:
            raise ValueError("No captions available for this video")
        
        # Read and process captions
        with open(captions_path, 'r', encoding='utf-8') as f:
            captions_text = f.read()
        
        # Simple SRT to text conversion
        import re
        text_lines = []
        for line in captions_text.split('\n'):
            line = line.strip()
            if line and not re.match(r'^\d+$', line) and not re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                text_lines.append(line)
        
        transcript_text = ' '.join(text_lines)
        
        return {
            'text': transcript_text,
            'language': 'en',  # Default assumption
            'language_probability': 1.0,
            'segments': [],
            'duration': event.video_info.duration
        }
    
    def handle_error(self, event: VideoDownloadedEvent, error: Exception):
        """Handle transcription errors by emitting error event."""
        error_event = TranscriptProcessingErrorEvent(
            video_id=event.video_id,
            error_message=str(error),
            error_type=type(error).__name__,
            transcription_method=self.transcription_method,
            source=self.name
        )
        self.publish_event(error_event) 