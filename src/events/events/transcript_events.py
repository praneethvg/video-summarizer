"""
Transcript-related events for the processing pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from ..base.event import Event


@dataclass
class TranscriptSegment:
    """A segment of transcribed text with timing information."""
    start: float
    end: float
    text: str
    confidence: float = 0.0


@dataclass
class TranscriptGeneratedEvent(Event):
    """Event emitted when a transcript has been generated."""
    video_id: str
    transcript_text: str
    language: str = "en"
    language_probability: float = 0.0
    segments: List[TranscriptSegment] = field(default_factory=list)
    transcription_method: str = "whisper"  # whisper, captions, etc.
    processing_duration: float = 0.0
    
    def __init__(self, video_id: str, transcript_text: str, language: str = "en", language_probability: float = 0.0, segments: List[TranscriptSegment] = None, transcription_method: str = "whisper", processing_duration: float = 0.0, *, source: str = "", metadata: dict = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.transcript_text = transcript_text
        self.language = language
        self.language_probability = language_probability
        self.segments = segments if segments is not None else []
        self.transcription_method = transcription_method
        self.processing_duration = processing_duration
        self.__post_init__()
    
    def __post_init__(self):
        super().__post_init__()
        # Convert segments to TranscriptSegment objects if they're dicts
        if self.segments and isinstance(self.segments[0], dict):
            self.segments = [TranscriptSegment(**seg) for seg in self.segments]


@dataclass
class TranscriptProcessingErrorEvent(Event):
    """Event emitted when transcript processing fails."""
    video_id: str
    error_message: str
    error_type: str = "unknown"
    transcription_method: str = "unknown"
    
    def __init__(self, video_id: str, error_message: str, error_type: str = "unknown", transcription_method: str = "unknown", *, source: str = "", metadata: dict = None):
        super().__init__(source=source, metadata=metadata)
        self.video_id = video_id
        self.error_message = error_message
        self.error_type = error_type
        self.transcription_method = transcription_method
        self.__post_init__() 