"""
Video-related events for the processing pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

from ..base.event import Event


@dataclass
class VideoInfo:
    """Information about a video."""
    title: str
    duration: float
    uploader: str
    view_count: int = 0
    description: str = ""
    language: str = "en"
    tags: list = field(default_factory=list)


@dataclass
class VideoDiscoveredEvent(Event):
    """Event emitted when a video is discovered (URL provided)."""
    url: str
    title: str = ""
    provider: str = "unknown"
    video_info: Optional[VideoInfo] = None
    
    def __init__(self, url: str, title: str = "", provider: str = "unknown", video_info: Optional[VideoInfo] = None, *, source: str = "", metadata: Optional[dict] = None):
        super().__init__(source=source, metadata=metadata)
        self.url = url
        self.title = title
        self.provider = provider
        self.video_info = video_info
        self.__post_init__()
    
    def __post_init__(self):
        super().__post_init__()
        if not self.title and self.video_info:
            self.title = self.video_info.title


@dataclass
class VideoDownloadedEvent(Event):
    """Event emitted when a video has been downloaded."""
    video_id: str
    audio_path: str
    video_info: VideoInfo
    url: str = ""  # Original video URL
    download_duration: float = 0.0
    
    def __init__(self, video_id: str, audio_path: str, video_info: VideoInfo, url: str = "", download_duration: float = 0.0, *, source: str = "", metadata: Optional[dict] = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.audio_path = audio_path
        self.video_info = video_info
        self.url = url
        self.download_duration = download_duration
        self.__post_init__()
    
    def __post_init__(self):
        super().__post_init__()
        # Ensure audio_path is a string
        if isinstance(self.audio_path, Path):
            self.audio_path = str(self.audio_path)


@dataclass
class VideoProcessingErrorEvent(Event):
    """Event emitted when video processing fails."""
    video_id: str
    error_message: str
    error_type: str = "unknown"
    stage: str = "unknown"  # download, transcription, etc.
    
    def __init__(self, video_id: str, error_message: str, error_type: str = "unknown", stage: str = "unknown", *, source: str = "", metadata: Optional[dict] = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.error_message = error_message
        self.error_type = error_type
        self.stage = stage
        self.__post_init__() 