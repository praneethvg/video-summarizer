"""
Event Bus for publishing and subscribing to events.
"""

from collections import defaultdict
from typing import Callable, Dict, List, Type, Any
import logging
from rich.console import Console

from .event import Event

console = Console()
logger = logging.getLogger(__name__)


class EventBus:
    """Simple event bus for publishing and subscribing to events."""
    
    def __init__(self):
        self.handlers: Dict[Type[Event], List[Callable]] = defaultdict(list)
        self.event_history: List[Event] = []
        self.max_history = 1000  # Keep last 1000 events for debugging
    
    def subscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        """Subscribe a handler to an event type."""
        self.handlers[event_type].append(handler)
        handler_name = getattr(handler, 'name', handler.__class__.__name__)
        logger.info(f"Subscribed handler {handler_name} to {event_type.__name__}")
    
    def unsubscribe(self, event_type: Type[Event], handler: Callable[[Event], None]):
        """Unsubscribe a handler from an event type."""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                handler_name = getattr(handler, 'name', handler.__class__.__name__)
                logger.info(f"Unsubscribed handler {handler_name} from {event_type.__name__}")
            except ValueError:
                handler_name = getattr(handler, 'name', handler.__class__.__name__)
                logger.warning(f"Handler {handler_name} not found for {event_type.__name__}")
    
    def publish(self, event: Event):
        """Publish an event to all subscribed handlers."""
        event_type = type(event)
        
        # Store event in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
        
        # Log event
        logger.info(f"Publishing {event_type.__name__}: {event.event_id}")
        console.print(f"[blue]📡 Event: {event_type.__name__}[/blue]")
        
        # Notify all handlers
        handlers = self.handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
                handler_name = getattr(handler, 'name', handler.__class__.__name__)
                logger.debug(f"Handler {handler_name} processed {event_type.__name__}")
            except Exception as e:
                handler_name = getattr(handler, 'name', handler.__class__.__name__)
                logger.error(f"Error in handler {handler_name} for {event_type.__name__}: {e}")
                console.print(f"[red]❌ Handler error: {e}[/red]")
    
    def get_event_history(self, event_type: Type[Event] = None) -> List[Event]:
        """Get event history, optionally filtered by event type."""
        if event_type:
            return [event for event in self.event_history if isinstance(event, event_type)]
        return self.event_history.copy()
    
    def clear_history(self):
        """Clear event history."""
        self.event_history.clear()
        logger.info("Event history cleared")
    
    def get_subscriber_count(self, event_type: Type[Event]) -> int:
        """Get number of subscribers for an event type."""
        return len(self.handlers.get(event_type, []))
    
    def list_subscribers(self) -> Dict[str, int]:
        """List all event types and their subscriber counts."""
        return {event_type.__name__: len(handlers) 
                for event_type, handlers in self.handlers.items()} 