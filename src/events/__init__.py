"""
Event-driven system for video processing pipeline.
"""

from .base.event import Event
from .base.event_bus import EventBus
from .events.video_events import VideoDiscoveredEvent, VideoDownloadedEvent, VideoProcessingErrorEvent
from .events.transcript_events import TranscriptGeneratedEvent, TranscriptProcessingErrorEvent
from .events.summary_events import SummaryCreatedEvent, SummaryProcessingErrorEvent

__all__ = [
    'Event',
    'EventBus',
    'VideoDiscoveredEvent',
    'VideoDownloadedEvent',
    'VideoProcessingErrorEvent',
    'TranscriptGeneratedEvent',
    'TranscriptProcessingErrorEvent',
    'SummaryCreatedEvent',
    'SummaryProcessingErrorEvent'
] 