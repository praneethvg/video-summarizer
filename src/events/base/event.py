"""
Base Event class for the event-driven system.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class Event(ABC):
    """Base class for all events in the system."""
    # Event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    timestamp: datetime = field(default_factory=datetime.now, init=False)
    
    def __init__(self, *args, source: str = "", metadata: Optional[Dict[str, Any]] = None, **kwargs):
        self.source = source
        self.metadata = metadata if metadata is not None else {}
        super().__init__()
    
    def __post_init__(self):
        if not hasattr(self, 'event_id') or not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not hasattr(self, 'timestamp') or not self.timestamp:
            self.timestamp = datetime.now()
        if not hasattr(self, 'metadata'):
            self.metadata = {}
        if not hasattr(self, 'source'):
            self.source = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'metadata': self.metadata,
            'event_type': self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        raise NotImplementedError("Subclasses must implement from_dict") 