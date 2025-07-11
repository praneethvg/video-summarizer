"""
Summary-related events for the processing pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from ..base.event import Event


@dataclass
class SummaryCreatedEvent(Event):
    """Event emitted when a summary has been created."""
    video_id: str
    summary_text: str
    format: str = "text"  # text, markdown, json, pdf
    summary_style: str = "comprehensive"  # comprehensive, bullet_points, etc.
    summary_length: str = "medium"  # short, medium, long
    word_count: int = 0
    model_used: str = ""
    tokens_used: Optional[int] = None
    processing_duration: float = 0.0
    output_path: Optional[str] = None  # Path to saved summary file
    
    def __init__(self, video_id: str, summary_text: str, format: str = "text", summary_style: str = "comprehensive", summary_length: str = "medium", word_count: int = 0, model_used: str = "", tokens_used: Optional[int] = None, processing_duration: float = 0.0, output_path: Optional[str] = None, *, source: str = "", metadata: dict = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.summary_text = summary_text
        self.format = format
        self.summary_style = summary_style
        self.summary_length = summary_length
        self.word_count = word_count
        self.model_used = model_used
        self.tokens_used = tokens_used
        self.processing_duration = processing_duration
        self.output_path = output_path
        self.__post_init__()
    
    def __post_init__(self):
        super().__post_init__()
        if not self.word_count:
            self.word_count = len(self.summary_text.split())


@dataclass
class SummaryProcessingErrorEvent(Event):
    """Event emitted when summary processing fails."""
    video_id: str
    error_message: str
    error_type: str = "unknown"
    summary_style: str = "unknown"
    format: str = "unknown"
    
    def __init__(self, video_id: str, error_message: str, error_type: str = "unknown", summary_style: str = "unknown", format: str = "unknown", *, source: str = "", metadata: dict = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.error_message = error_message
        self.error_type = error_type
        self.summary_style = summary_style
        self.format = format
        self.__post_init__() 