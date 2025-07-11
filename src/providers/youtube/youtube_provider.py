"""
YouTube content provider that emits events for video processing.
"""

import re
from typing import Optional
from rich.console import Console

from src.providers.base.content_provider import ContentProvider
from src.events import EventBus, VideoDiscoveredEvent
from src.events.events.video_events import VideoInfo
from src.config import Config

console = Console()


class YouTubeProvider(ContentProvider):
    """YouTube content provider that emits VideoDiscoveredEvent."""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus, "YouTubeProvider")
        self.youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+'
        ]
    
    def process_url(self, url: str) -> None:
        """
        Process a YouTube URL and emit VideoDiscoveredEvent.
        
        Args:
            url: YouTube video URL
        """
        if not self._is_valid_youtube_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        # Get video information
        video_info = self._get_video_info(url)
        
        # Emit video discovered event
        self.emit_video_discovered(
            url=url,
            title=video_info.title,
            provider="youtube",
            video_info=video_info
        )
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """Validate YouTube URL."""
        for pattern in self.youtube_patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def _get_video_info(self, url: str) -> VideoInfo:
        """Get video information using existing downloader logic."""
        # Import here to avoid circular imports
        from src.downloader import YouTubeDownloader
        
        downloader = YouTubeDownloader(Config.TEMP_DIR)
        info = downloader.get_video_info(url)
        
        return VideoInfo(
            title=info.get('title', 'Unknown'),
            duration=info.get('duration', 0),
            uploader=info.get('uploader', 'Unknown'),
            view_count=info.get('view_count', 0),
            description=info.get('description', ''),
            language='en'  # Default assumption
        )
    
    def get_capabilities(self) -> list:
        """Get list of capabilities this provider supports."""
        return ['url_processing', 'video_info_extraction'] 