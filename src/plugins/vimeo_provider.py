"""
Vimeo provider plugin for the YouTube summarizer.
"""

import re
from typing import List
from rich.console import Console

from src.plugins.base.plugin_base import ProviderPlugin, PluginInfo
from src.events import VideoDiscoveredEvent
from src.events.events.video_events import VideoInfo

console = Console()


class VimeoProvider(ProviderPlugin):
    """Vimeo content provider plugin."""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="vimeo_provider",
            version="1.0.0",
            description="Provider for Vimeo videos",
            author="YouTube Summarizer Team",
            plugin_type="provider",
            entry_point="VimeoProvider",
            config_schema={
                "api_key": {"type": "string", "required": False},
                "download_quality": {"type": "string", "default": "best"}
            }
        )
    
    def get_supported_urls(self) -> List[str]:
        return [
            r'(?:https?://)?(?:www\.)?vimeo\.com/\d+',
            r'(?:https?://)?(?:www\.)?vimeo\.com/channels/\w+/\d+',
            r'(?:https?://)?(?:www\.)?vimeo\.com/groups/\w+/videos/\d+'
        ]
    
    def can_handle_url(self, url: str) -> bool:
        for pattern in self.supported_urls:
            if re.match(pattern, url):
                return True
        return False
    
    def process_url(self, url: str) -> None:
        """Process a Vimeo URL and emit VideoDiscoveredEvent."""
        if not self.can_handle_url(url):
            raise ValueError(f"Invalid Vimeo URL: {url}")
        
        # Get video information using the downloader
        video_info = self._get_video_info(url)
        
        # Emit video discovered event
        event = VideoDiscoveredEvent(
            url=url,
            title=video_info.title,
            provider="vimeo",
            video_info=video_info,
            source=self.plugin_info.name
        )
        
        console.print(f"[blue]🔍 Vimeo provider discovered video: {video_info.title}[/blue]")
        self.event_bus.publish(event)
    
    def _get_video_info(self, url: str) -> VideoInfo:
        """Get video information using the downloader registry."""
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
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from Vimeo URL."""
        patterns = [
            r'vimeo\.com/(\d+)',
            r'vimeo\.com/channels/\w+/(\d+)',
            r'vimeo\.com/groups/\w+/videos/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback: use URL hash
        return str(hash(url))[-8:]
    
    def get_capabilities(self) -> List[str]:
        return ['url_processing', 'video_info_extraction', 'vimeo_api'] 