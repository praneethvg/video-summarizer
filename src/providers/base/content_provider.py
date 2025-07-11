"""
Base ContentProvider interface for the event-driven system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from rich.console import Console

from src.events import EventBus, VideoDiscoveredEvent
from src.events.events.video_events import VideoInfo

console = Console()


class ContentProvider(ABC):
    """Base class for content providers that emit events."""
    
    def __init__(self, event_bus: EventBus, name: str = None):
        self.event_bus = event_bus
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def process_url(self, url: str) -> None:
        """
        Process a URL and emit appropriate events.
        
        Args:
            url: The URL to process
        """
        pass
    
    def emit_video_discovered(self, url: str, title: str = "", 
                            provider: str = "unknown", 
                            video_info: Optional[VideoInfo] = None) -> VideoDiscoveredEvent:
        """
        Emit a VideoDiscoveredEvent.
        
        Args:
            url: The video URL
            title: Video title
            provider: Provider name
            video_info: Additional video information
            
        Returns:
            The created event
        """
        event = VideoDiscoveredEvent(
            url=url,
            title=title,
            provider=provider,
            video_info=video_info,
            source=self.name
        )
        
        console.print(f"[blue]🔍 {self.name} discovered video: {title or url}[/blue]")
        self.event_bus.publish(event)
        return event
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            'name': self.name,
            'type': self.__class__.__name__,
            'capabilities': self.get_capabilities()
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this provider supports."""
        return ['url_processing'] 