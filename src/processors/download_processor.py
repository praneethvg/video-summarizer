"""
Download processor that handles VideoDiscoveredEvent and emits VideoDownloadedEvent.
"""

import time
from pathlib import Path
from rich.console import Console

from src.events.handlers.event_handler import EventProcessor
from src.events import VideoDiscoveredEvent, VideoDownloadedEvent, VideoProcessingErrorEvent
from src.events.events.video_events import VideoInfo
from src.config import Config
from src.downloaders import DownloaderRegistry

console = Console()


class DownloadProcessor(EventProcessor):
    """Processor that downloads videos when VideoDiscoveredEvent is received."""
    
    def __init__(self, event_bus):
        super().__init__(event_bus, "DownloadProcessor")
        self.downloader_registry = DownloaderRegistry()
    
    def handle(self, event: VideoDiscoveredEvent):
        """
        Handle VideoDiscoveredEvent by downloading the video.
        
        Args:
            event: VideoDiscoveredEvent containing video information
        """
        console.print(f"[blue]⬇️  Downloading video: {event.title or event.url}[/blue]")
        
        start_time = time.time()
        
        try:
            # Get appropriate downloader for this URL
            downloader = self.downloader_registry.get_downloader_for_url(event.url)
            if not downloader:
                raise Exception(f"No downloader available for URL: {event.url}")
            
            # Download audio
            audio_path = downloader.download_audio(event.url)
            download_duration = time.time() - start_time
            
            # Extract video ID from URL
            video_id = self._extract_video_id(event.url)
            
            # Create video info if not provided
            video_info = event.video_info or VideoInfo(
                title=event.title,
                duration=0,
                uploader="Unknown"
            )
            
            # Emit VideoDownloadedEvent
            download_event = VideoDownloadedEvent(
                video_id=video_id,
                audio_path=audio_path,
                video_info=video_info,
                url=event.url,  # Pass the original URL
                download_duration=download_duration,
                source=self.name
            )
            
            self.publish_event(download_event)
            return audio_path
            
        except Exception as e:
            # Emit error event
            error_event = VideoProcessingErrorEvent(
                video_id=self._extract_video_id(event.url),
                error_message=str(e),
                error_type=type(e).__name__,
                stage="download",
                source=self.name
            )
            self.publish_event(error_event)
            raise
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL."""
        import re
        
        # YouTube video ID patterns
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback: use URL hash
        return str(hash(url))[-8:]
    
    def handle_error(self, event: VideoDiscoveredEvent, error: Exception):
        """Handle download errors by emitting error event."""
        error_event = VideoProcessingErrorEvent(
            video_id=self._extract_video_id(event.url),
            error_message=str(error),
            error_type=type(error).__name__,
            stage="download",
            source=self.name
        )
        self.publish_event(error_event) 