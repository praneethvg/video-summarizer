"""
Plugin manager for discovering, loading, and managing plugins.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.events import EventBus, Event
from src.plugins.base.plugin_base import Plugin, ProcessorPlugin, ProviderPlugin, PluginInfo, PluginLoader

console = Console()


class PluginManager:
    """Manages plugin discovery, loading, and lifecycle."""
    
    def __init__(self, event_bus: EventBus, plugins_dir: str = "plugins"):
        self.event_bus = event_bus
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.enabled_plugins: List[str] = []  # Changed from disabled_plugins
        self.load_all_plugins_by_default: bool = True  # Load all discovered plugins by default
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Load plugin configurations
        self._load_plugin_configs()
    
    def discover_plugins(self) -> List[PluginInfo]:
        """Discover all available plugins."""
        plugin_infos = []
        
        if not self.plugins_dir.exists():
            console.print(f"[yellow]⚠️  Plugins directory not found: {self.plugins_dir}[/yellow]")
            return plugin_infos
        
        # Look for Python files in the plugins directory
        for plugin_file in self.plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue  # Skip private files
            
            try:
                plugin_info = PluginLoader.load_plugin_info_from_file(plugin_file)
                plugin_infos.append(plugin_info)
                console.print(f"[green]✅ Discovered plugin: {plugin_info.name} v{plugin_info.version}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to load plugin {plugin_file.name}: {e}[/red]")
        
        return plugin_infos
    
    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Load a specific plugin by name."""
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        
        if not plugin_file.exists():
            console.print(f"[red]❌ Plugin file not found: {plugin_file}[/red]")
            return False
        
        try:
            # Load plugin class
            plugin_class = PluginLoader.load_plugin_from_file(plugin_file)
            
            # Get plugin configuration
            plugin_config = config or self.plugin_configs.get(plugin_name, {})
            
            # Create plugin instance
            plugin = plugin_class(self.event_bus, plugin_config)
            
            # Initialize plugin
            if not plugin.initialize():
                console.print(f"[red]❌ Failed to initialize plugin: {plugin_name}[/red]")
                return False
            
            # Store plugin
            self.plugins[plugin_name] = plugin
            
            console.print(f"[green]✅ Loaded plugin: {plugin_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to load plugin {plugin_name}: {e}[/red]")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        plugin_infos = self.discover_plugins()
        
        for plugin_info in plugin_infos:
            # Check if plugin should be loaded based on enabled list
            should_load = (not self.enabled_plugins or  # If no enabled list, load all
                          plugin_info.name in self.enabled_plugins)  # Or if explicitly enabled
            
            if not should_load:
                console.print(f"[yellow]⏭️  Skipping disabled plugin: {plugin_info.name}[/yellow]")
                results[plugin_info.name] = False
                continue
            
            success = self.load_plugin(plugin_info.name)
            results[plugin_info.name] = success
            
            # Add to enabled list if successfully loaded and not already there
            if success and plugin_info.name not in self.enabled_plugins:
                self.enabled_plugins.append(plugin_info.name)
        
        return results
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            console.print(f"[yellow]⚠️  Plugin not loaded: {plugin_name}[/yellow]")
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.cleanup()
            del self.plugins[plugin_name]
            
            console.print(f"[green]✅ Unloaded plugin: {plugin_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to unload plugin {plugin_name}: {e}[/red]")
            return False
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: str) -> List[Plugin]:
        """Get all plugins of a specific type."""
        return [plugin for plugin in self.plugins.values() 
                if plugin.plugin_info.plugin_type == plugin_type]
    
    def get_processor_plugins(self) -> List[ProcessorPlugin]:
        """Get all processor plugins."""
        return [plugin for plugin in self.plugins.values() 
                if isinstance(plugin, ProcessorPlugin)]
    
    def get_provider_plugins(self) -> List[ProviderPlugin]:
        """Get all provider plugins."""
        return [plugin for plugin in self.plugins.values() 
                if isinstance(plugin, ProviderPlugin)]
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enable()
            if plugin_name not in self.enabled_plugins:
                self.enabled_plugins.append(plugin_name)
            console.print(f"[green]✅ Enabled plugin: {plugin_name}[/green]")
            return True
        else:
            console.print(f"[red]❌ Plugin not found: {plugin_name}[/red]")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].disable()
            if plugin_name in self.enabled_plugins:
                self.enabled_plugins.remove(plugin_name)
            console.print(f"[yellow]⚠️  Disabled plugin: {plugin_name}[/yellow]")
            return True
        else:
            console.print(f"[red]❌ Plugin not found: {plugin_name}[/red]")
            return False
    
    def list_plugins(self) -> None:
        """List all loaded plugins."""
        if not self.plugins:
            console.print("[yellow]No plugins loaded[/yellow]")
            return
        
        table = Table(title="Loaded Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Version", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Config", style="blue")
        table.add_column("Description", style="white")
        
        for name, plugin in self.plugins.items():
            # Determine status
            if plugin.is_enabled:
                status = "✅ Enabled"
            else:
                status = "❌ Disabled"
            
            # Show if plugin is in enabled list
            config_status = "📋 Listed" if name in self.enabled_plugins else "🚫 Not Listed"
            
            table.add_row(
                name,
                plugin.plugin_info.plugin_type,
                plugin.plugin_info.version,
                status,
                config_status,
                plugin.plugin_info.description[:40] + "..." if len(plugin.plugin_info.description) > 40 else plugin.plugin_info.description
            )
        
        console.print(table)
        
        # Show configuration info
        console.print(f"\n[bold]Configuration:[/bold]")
        console.print(f"  Load all plugins by default: {'✅ Yes' if self.load_all_plugins_by_default else '❌ No'}")
        console.print(f"  Enabled plugins in config: {len(self.enabled_plugins)}")
        if self.enabled_plugins:
            console.print(f"  Enabled: {', '.join(self.enabled_plugins)}")
    
    def _load_plugin_configs(self) -> None:
        """Load plugin configurations from config files."""
        config_file = self.plugins_dir / "config.yaml"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                if config_data:
                    # Load plugin-specific configurations
                    if 'plugins' in config_data:
                        for plugin_name, config in config_data['plugins'].items():
                            self.plugin_configs[plugin_name] = config
                    
                    # Load enabled plugins list
                    if 'enabled_plugins' in config_data:
                        self.enabled_plugins = config_data['enabled_plugins']
                    
                    # Load load-all-by-default setting
                    if 'load_all_plugins_by_default' in config_data:
                        self.load_all_plugins_by_default = config_data['load_all_plugins_by_default']
                
                console.print(f"[green]✅ Loaded plugin configurations from {config_file}[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Failed to load plugin configs: {e}[/red]")
    
    def save_plugin_configs(self) -> None:
        """Save plugin configurations to config file."""
        config_file = self.plugins_dir / "config.yaml"
        
        try:
            config_data = {
                'plugins': self.plugin_configs,
                'enabled_plugins': self.enabled_plugins,
                'load_all_plugins_by_default': self.load_all_plugins_by_default
            }
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
            
            console.print(f"[green]✅ Saved plugin configurations to {config_file}[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to save plugin configs: {e}[/red]")
    
    def get_plugin_status(self) -> Dict[str, Any]:
        """Get status information about all plugins."""
        return {
            'total_plugins': len(self.plugins),
            'enabled_plugins': len([p for p in self.plugins.values() if p.is_enabled]),
            'disabled_plugins': len([p for p in self.plugins.values() if not p.is_enabled]),
            'processor_plugins': len(self.get_processor_plugins()),
            'provider_plugins': len(self.get_provider_plugins()),
            'load_all_by_default': self.load_all_plugins_by_default,
            'plugins': {
                name: {
                    'type': plugin.plugin_info.plugin_type,
                    'version': plugin.plugin_info.version,
                    'enabled': plugin.is_enabled,
                    'description': plugin.plugin_info.description
                }
                for name, plugin in self.plugins.items()
            }
        }
    
    def enable_all_plugins(self) -> None:
        """Enable all loaded plugins."""
        for plugin_name in self.plugins.keys():
            self.enable_plugin(plugin_name)
    
    def disable_all_plugins(self) -> None:
        """Disable all loaded plugins."""
        for plugin_name in self.plugins.keys():
            self.disable_plugin(plugin_name)
    
    def set_load_all_plugins_by_default(self, enabled: bool) -> None:
        """Set whether all discovered plugins should be loaded by default."""
        self.load_all_plugins_by_default = enabled
        console.print(f"[green]✅ Load all plugins by default: {'enabled' if enabled else 'disabled'}[/green]")
    
    def get_enabled_plugins_list(self) -> List[str]:
        """Get list of enabled plugin names."""
        return self.enabled_plugins.copy()
    
    def get_disabled_plugins_list(self) -> List[str]:
        """Get list of disabled plugin names."""
        return [name for name in self.plugins.keys() if name not in self.enabled_plugins] 