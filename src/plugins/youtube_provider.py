"""
YouTube provider plugin for the video summarizer.
"""

import re
from typing import List
from rich.console import Console

from src.plugins.base.plugin_base import ProviderPlugin, PluginInfo
from src.events import VideoDiscoveredEvent
from src.events.events.video_events import VideoInfo
from src.config import Config

console = Console()


class YouTubeProvider(ProviderPlugin):
    """YouTube content provider plugin."""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="youtube_provider",
            version="1.0.0",
            description="Provider for YouTube videos",
            author="YouTube Summarizer Team",
            plugin_type="provider",
            entry_point="YouTubeProvider",
            config_schema={
                "download_quality": {"type": "string", "default": "best"},
                "extract_audio": {"type": "boolean", "default": True}
            }
        )
    
    def get_supported_urls(self) -> List[str]:
        return [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+'
        ]
    
    def can_handle_url(self, url: str) -> bool:
        for pattern in self.supported_urls:
            if re.match(pattern, url):
                return True
        return False
    
    def process_url(self, url: str) -> None:
        """Process a YouTube URL and emit VideoDiscoveredEvent."""
        if not self.can_handle_url(url):
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        # Get video information
        video_info = self._get_video_info(url)
        
        # Emit video discovered event
        event = VideoDiscoveredEvent(
            url=url,
            title=video_info.title,
            provider="youtube",
            video_info=video_info,
            source=self.plugin_info.name
        )
        
        console.print(f"[blue]🔍 YouTube provider discovered video: {video_info.title}[/blue]")
        self.event_bus.publish(event)
    
    def _get_video_info(self, url: str) -> VideoInfo:
        """Get video information using existing downloader logic."""
        # Import here to avoid circular imports
        from src.downloaders import DownloaderRegistry
        
        registry = DownloaderRegistry()
        downloader = registry.get_downloader_for_url(url)
        if not downloader:
            raise Exception(f"No downloader available for URL: {url}")
        
        info = downloader.get_video_info(url)
        
        return VideoInfo(
            title=info.get('title', 'Unknown'),
            duration=info.get('duration', 0),
            uploader=info.get('uploader', 'Unknown'),
            view_count=info.get('view_count', 0),
            description=info.get('description', ''),
            language='en'  # Default assumption
        )
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this provider supports."""
        return ['url_processing', 'video_info_extraction', 'youtube_api'] 