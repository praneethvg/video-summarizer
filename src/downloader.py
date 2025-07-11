"""
Generic video downloader interface.
Handles downloading videos and extracting audio for transcription.
"""

# Import from the new downloaders package structure
from src.downloaders import (
    VideoDownloader,
    YouTubeDownloader,
    VimeoDownloader,
    DownloaderRegistry
)

# Re-export for backward compatibility
__all__ = [
    'VideoDownloader',
    'YouTubeDownloader',
    'VimeoDownloader', 
    'DownloaderRegistry'
]
