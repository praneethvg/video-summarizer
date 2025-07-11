"""
Base video downloader interface.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console

console = Console()

class VideoDownloader(ABC):
    """Abstract base class for video downloaders."""
    
    def __init__(self, temp_dir: str = "./temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Check if this downloader can handle the given URL."""
        pass
    
    @abstractmethod
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading."""
        pass
    
    @abstractmethod
    def download_audio(self, url: str, output_filename: Optional[str] = None) -> str:
        """Download audio from video."""
        pass
    
    @abstractmethod
    def download_captions(self, url: str, output_filename: Optional[str] = None, lang: str = "en", prefer_manual: bool = True) -> Optional[str]:
        """Download closed captions from video."""
        pass
    
    @abstractmethod
    def list_available_captions(self, url: str) -> Dict[str, Any]:
        """List available captions for video."""
        pass
    
    def cleanup_temp_files(self, file_path: str):
        """Clean up temporary downloaded files."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                console.print(f"[green]Cleaned up: {file_path}[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not clean up {file_path}: {e}[/yellow]")
    
    def get_download_progress(self, url: str) -> Dict[str, Any]:
        """Get download progress information."""
        info = self.get_video_info(url)
        duration_minutes = info['duration'] / 60 if info['duration'] else 0
        
        return {
            'title': info['title'],
            'duration_minutes': round(duration_minutes, 1),
            'uploader': info['uploader'],
            'estimated_download_time': max(1, duration_minutes * 0.1),  # Rough estimate
            'estimated_transcription_time': max(2, duration_minutes * 0.2)  # Rough estimate
        } 