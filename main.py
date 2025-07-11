#!/usr/bin/env python3
"""
Plugin-Driven YouTube Video Summarizer - Main Application
Uses the new plugin system for extensible video processing.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import our modules
from src.config import Config
from src.events import EventBus
from src.processors import DownloadProcessor, TranscriptionProcessor, SummarizationProcessor
from src.plugin_manager import PluginManager

console = Console()

def print_banner():
    """Print application banner."""
    banner = """
🎥 Plugin-Driven YouTube Video Summarizer 🎥
   Powered by Event-Driven Architecture + Plugin System
   YouTube → Download → Transcribe → Summarize → [Plugins]
    """
    console.print(Panel(banner, style="bold blue"))

def setup_plugin_pipeline(args) -> tuple[EventBus, PluginManager]:
    """Set up the event-driven pipeline with plugins."""
    event_bus = EventBus()
    
    # Create plugin manager
    plugin_manager = PluginManager(event_bus, plugins_dir="src/plugins")
    
    # Load all plugins
    console.print("\n[bold blue]🔌 Loading Plugins...[/bold blue]")
    plugin_results = plugin_manager.load_all_plugins()
    
    # Show plugin loading results
    table = Table(title="Plugin Loading Results")
    table.add_column("Plugin", style="cyan")
    table.add_column("Status", style="green")
    
    for plugin_name, success in plugin_results.items():
        status = "✅ Loaded" if success else "❌ Failed"
        table.add_row(plugin_name, status)
    
    console.print(table)
    
    # Create core processors (these are built-in, not plugins)
    console.print("\n[bold blue]⚙️  Setting up Core Processors...[/bold blue]")
    download_processor = DownloadProcessor(event_bus)
    transcription_processor = TranscriptionProcessor(
        event_bus, 
        whisper_model=args.whisper_model,
        transcription_method=args.transcription_method
    )
    summarization_processor = SummarizationProcessor(
        event_bus,
        summary_style=args.summary_style,
        summary_length=args.summary_length,
        output_format=args.format
    )
    
    # Subscribe core processors to events
    from src.events import VideoDiscoveredEvent, VideoDownloadedEvent, TranscriptGeneratedEvent
    
    event_bus.subscribe(VideoDiscoveredEvent, download_processor)
    event_bus.subscribe(VideoDownloadedEvent, transcription_processor)
    event_bus.subscribe(TranscriptGeneratedEvent, summarization_processor)
    
    console.print(f"[green]✅ Event pipeline configured with {len(event_bus.handlers)} event types[/green]")
    
    return event_bus, plugin_manager

def process_single_video(url: str, args, event_bus: EventBus, plugin_manager: PluginManager) -> bool:
    """Process a single video using the plugin-driven system."""
    try:
        # Get all provider plugins (including YouTube)
        provider_plugins = plugin_manager.get_provider_plugins()
        
        if not provider_plugins:
            console.print(f"[red]❌ No provider plugins available[/red]")
            return False
        
        # Check if any provider can handle this URL
        url_handled = False
        
        for provider_plugin in provider_plugins:
            if provider_plugin.can_handle_url(url):
                console.print(f"[blue]🔌 Using provider: {provider_plugin.plugin_info.name}[/blue]")
                provider_plugin.process_url(url)
                url_handled = True
                break
        
        # If no provider can handle it, error out
        if not url_handled:
            console.print(f"[red]❌ No provider can handle URL: {url}[/red]")
            console.print(f"[yellow]Available providers: {[p.plugin_info.name for p in provider_plugins]}[/yellow]")
            return False
        
        console.print(f"\n[bold green]🎉 Plugin-driven processing initiated![/bold green]")
        console.print(f"[yellow]💡 Check the output directory for results.[/yellow]")
        
        # Show plugin status
        if args.show_plugins:
            console.print("\n[bold blue]🔌 Active Plugins:[/bold blue]")
            plugin_manager.list_plugins()
        
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Error in plugin-driven processing: {e}[/red]")
        return False

def process_multiple_videos(urls: List[str], args, event_bus: EventBus, plugin_manager: PluginManager) -> bool:
    """Process multiple videos using the plugin-driven system."""
    console.print(f"\n[blue]📋 Processing {len(urls)} videos with plugin-driven system...[/blue]")
    
    success_count = 0
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        console.print(f"\n[bold blue]Processing video {i}/{len(urls)}[/bold blue]")
        console.print(f"URL: {url}")
        
        if process_single_video(url, args, event_bus, plugin_manager):
            success_count += 1
        else:
            failed_urls.append(url)
    
    # Summary
    console.print(f"\n[bold green]📊 Plugin-Driven Processing Summary:[/bold green]")
    console.print(f"✅ Successful: {success_count}")
    console.print(f"❌ Failed: {len(failed_urls)}")
    
    if failed_urls:
        console.print(f"\n[yellow]Failed URLs:[/yellow]")
        for url in failed_urls:
            console.print(f"  - {url}")
    
    return success_count == len(urls)

def list_plugins(plugin_manager: PluginManager) -> None:
    """List all available and loaded plugins."""
    console.print("\n[bold blue]🔌 Plugin Information[/bold blue]")
    
    # Show loaded plugins
    plugin_manager.list_plugins()
    
    # Show plugin status
    status = plugin_manager.get_plugin_status()
    console.print(f"\n[bold]Plugin Statistics:[/bold]")
    console.print(f"  Total Plugins: {status['total_plugins']}")
    console.print(f"  Enabled: {status['enabled_plugins']}")
    console.print(f"  Disabled: {status['disabled_plugins']}")
    console.print(f"  Processors: {status['processor_plugins']}")
    console.print(f"  Providers: {status['provider_plugins']}")

def main():
    """Main application entry point."""
    # Load and validate configuration
    Config.load()
    Config.validate()
    
    parser = argparse.ArgumentParser(
        description="Plugin-Driven YouTube Video Summarizer - Download, transcribe, and summarize videos with plugins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_plugin_driven.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  python main_plugin_driven.py --url "VIDEO_URL" --format pdf --summary-style structured
  python main_plugin_driven.py --urls "url1,url2,url3" --transcription-method captions
  python main_plugin_driven.py --list-plugins
        """
    )
    
    # URL arguments
    url_group = parser.add_mutually_exclusive_group(required=False)
    url_group.add_argument('--url', help='Single video URL')
    url_group.add_argument('--urls', help='Comma-separated list of video URLs')
    
    # Processing options
    parser.add_argument('--whisper-model', 
                       choices=['tiny', 'base', 'small', 'medium', 'large'],
                       default=Config.DEFAULT_WHISPER_MODEL,
                       help='Whisper model size (default: small)')
    
    parser.add_argument('--transcription-method',
                       choices=['whisper', 'captions'],
                       default='whisper',
                       help='Transcription method: whisper (AI transcription) or captions (YouTube closed captions)')
    
    parser.add_argument('--summary-style',
                       choices=['comprehensive', 'bullet_points', 'key_points', 'structured'],
                       default='comprehensive',
                       help='Summary style (default: comprehensive)')
    
    parser.add_argument('--summary-length',
                       choices=['short', 'medium', 'long'],
                       default=Config.DEFAULT_SUMMARY_LENGTH,
                       help='Summary length (default: medium)')
    
    parser.add_argument('--format',
                       choices=['text', 'markdown', 'json', 'pdf'],
                       default='text',
                       help='Output format (default: text)')
    
    parser.add_argument('--output-dir',
                       default=Config.OUTPUT_DIR,
                       help='Output directory (default: ./output)')
    
    # Plugin options
    parser.add_argument('--list-plugins',
                       action='store_true',
                       help='List all available plugins and exit')
    
    parser.add_argument('--show-plugins',
                       action='store_true',
                       help='Show plugin status after processing')
    
    parser.add_argument('--plugins-dir',
                       default='plugins',
                       help='Directory containing plugins (default: plugins)')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Set up plugin pipeline
    event_bus, plugin_manager = setup_plugin_pipeline(args)
    
    # Handle plugin listing
    if args.list_plugins:
        list_plugins(plugin_manager)
        sys.exit(0)
    
    # Check if URL is provided
    if not args.url and not args.urls:
        console.print("[red]❌ Error: Please provide either --url or --urls argument[/red]")
        parser.print_help()
        sys.exit(1)
    
    # Process URLs
    if args.url:
        # Single video
        success = process_single_video(args.url, args, event_bus, plugin_manager)
        sys.exit(0 if success else 1)
    
    else:
        # Multiple videos
        urls = [url.strip() for url in args.urls.split(',')]
        success = process_multiple_videos(urls, args, event_bus, plugin_manager)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 