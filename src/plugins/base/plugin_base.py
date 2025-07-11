"""
Base classes for the plugin system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Type
from pathlib import Path
import importlib.util
import inspect

from src.events import EventBus, Event


@dataclass
class PluginInfo:
    """Information about a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: str  # "processor" or "provider"
    entry_point: str  # Class name to instantiate
    config_schema: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class Plugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        self.event_bus = event_bus
        self.config = config or {}
        self.plugin_info = self.get_plugin_info()
        self._enabled = True
    
    @abstractmethod
    def get_plugin_info(self) -> PluginInfo:
        """Return plugin information."""
        pass
    
    def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        return True
    
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass
    
    def enable(self) -> None:
        """Enable the plugin."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False
    
    @property
    def is_enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value


class ProcessorPlugin(Plugin):
    """Base class for processor plugins."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        super().__init__(event_bus, config)
        self.event_types = self.get_event_types()
        self._register_handlers()
    
    @abstractmethod
    def get_event_types(self) -> List[Type[Event]]:
        """Return list of event types this processor handles."""
        pass
    
    def _register_handlers(self) -> None:
        """Register event handlers."""
        for event_type in self.event_types:
            self.event_bus.subscribe(event_type, self)
    
    def handle(self, event: Event) -> Any:
        """Handle an event. Override in subclasses."""
        if not self.is_enabled:
            return None
        return self.process_event(event)
    
    @abstractmethod
    def process_event(self, event: Event) -> Any:
        """Process an event. Override in subclasses."""
        pass


class ProviderPlugin(Plugin):
    """Base class for provider plugins."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        super().__init__(event_bus, config)
        self.supported_urls = self.get_supported_urls()
    
    @abstractmethod
    def get_supported_urls(self) -> List[str]:
        """Return list of URL patterns this provider supports."""
        pass
    
    @abstractmethod
    def can_handle_url(self, url: str) -> bool:
        """Check if this provider can handle the given URL."""
        pass
    
    @abstractmethod
    def process_url(self, url: str) -> None:
        """Process a URL and emit appropriate events."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this provider supports."""
        return ['url_processing']


class PluginLoader:
    """Utility class for loading plugins from files."""
    
    @staticmethod
    def load_plugin_from_file(file_path: Path) -> Type[Plugin]:
        """Load a plugin class from a Python file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")
        
        # Load the module
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin classes
        plugin_classes = []
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Plugin) and 
                obj != Plugin and 
                obj != ProcessorPlugin and 
                obj != ProviderPlugin):
                plugin_classes.append(obj)
        
        if not plugin_classes:
            raise ValueError(f"No plugin classes found in {file_path}")
        
        if len(plugin_classes) > 1:
            raise ValueError(f"Multiple plugin classes found in {file_path}. Only one per file is allowed.")
        
        return plugin_classes[0]
    
    @staticmethod
    def load_plugin_info_from_file(file_path: Path) -> PluginInfo:
        """Load plugin information from a plugin file."""
        plugin_class = PluginLoader.load_plugin_from_file(file_path)
        
        # Create a temporary instance to get plugin info
        # We'll use a mock event bus for this
        class MockEventBus:
            def subscribe(self, event_type, handler):
                pass
        
        temp_plugin = plugin_class(MockEventBus())
        return temp_plugin.get_plugin_info() 