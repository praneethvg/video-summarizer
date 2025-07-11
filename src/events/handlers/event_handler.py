"""
Base event handler interface and common functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from rich.console import Console

from ..base.event import Event

console = Console()
logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """Base class for event handlers."""
    
    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.processed_count = 0
        self.error_count = 0
    
    @abstractmethod
    def handle(self, event: Event) -> None:
        """Handle an event. Must be implemented by subclasses."""
        pass
    
    def on_success(self, event: Event, result: Any = None):
        """Called when event is processed successfully."""
        self.processed_count += 1
        logger.info(f"Handler {self.name} successfully processed {type(event).__name__}")
        console.print(f"[green]✅ {self.name} processed {type(event).__name__}[/green]")
    
    def on_error(self, event: Event, error: Exception):
        """Called when event processing fails."""
        self.error_count += 1
        logger.error(f"Handler {self.name} failed to process {type(event).__name__}: {error}")
        console.print(f"[red]❌ {self.name} failed: {error}[/red]")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get handler statistics."""
        return {
            'name': self.name,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': self.processed_count / (self.processed_count + self.error_count) if (self.processed_count + self.error_count) > 0 else 0
        }


class EventProcessor(EventHandler):
    """Base class for event processors that consume and produce events."""
    
    def __init__(self, event_bus, name: str = None):
        super().__init__(name)
        self.event_bus = event_bus
    
    def publish_event(self, event: Event):
        """Publish an event to the event bus."""
        self.event_bus.publish(event)
        logger.debug(f"Handler {self.name} published {type(event).__name__}")
    
    def handle_with_error_handling(self, event: Event):
        """Handle event with automatic error handling."""
        try:
            result = self.handle(event)
            self.on_success(event, result)
            return result
        except Exception as e:
            self.on_error(event, e)
            # Optionally publish error event
            self.handle_error(event, e)
            raise
    
    def handle_error(self, event: Event, error: Exception):
        """Handle processing errors. Override in subclasses to publish error events."""
        pass 