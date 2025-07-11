"""
Registry for managing different video downloaders.
"""

from typing import Optional
from rich.console import Console

from .base import VideoDownloader
from .youtube import YouTubeDownloader
from .vimeo import VimeoDownloader

console = Console()

class DownloaderRegistry:
    """Registry for managing different video downloaders."""
    
    def __init__(self):
        self.downloaders = []
        self._register_default_downloaders()
    
    def _register_default_downloaders(self):
        """Register default downloaders."""
        self.register_downloader(YouTubeDownloader())
        self.register_downloader(VimeoDownloader())
    
    def register_downloader(self, downloader: VideoDownloader):
        """Register a new downloader."""
        self.downloaders.append(downloader)
        console.print(f"[blue]Registered downloader: {downloader.__class__.__name__}[/blue]")
    
    def get_downloader_for_url(self, url: str) -> Optional[VideoDownloader]:
        """Get the appropriate downloader for a given URL."""
        for downloader in self.downloaders:
            if downloader.can_handle_url(url):
                return downloader
        return None
    
    def list_downloaders(self):
        """List all registered downloaders."""
        console.print("[bold blue]Registered Downloaders:[/bold blue]")
        for downloader in self.downloaders:
            console.print(f"  - {downloader.__class__.__name__}") 