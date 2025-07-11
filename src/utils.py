"""
Utility functions for the YouTube Summarizer.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and limit length
    filename = re.sub(r'\s+', ' ', filename).strip()
    return filename[:100]  # Limit length

def save_summary_to_file(summary_data: Dict[str, Any], output_path: str, format: str = "text"):
    """
    Save summary to file in specified format.
    
    Args:
        summary_data: Summary data dictionary
        output_path: Output file path
        format: Output format (text, markdown, json)
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if format == "json":
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
    
    elif format == "markdown":
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {summary_data.get('title', 'Video Summary')}\n\n")
            f.write(f"**Uploader:** {summary_data.get('uploader', 'Unknown')}\n")
            f.write(f"**Duration:** {summary_data.get('duration_minutes', 0):.1f} minutes\n")
            f.write(f"**Language:** {summary_data.get('language', 'Unknown')}\n")
            f.write(f"**Summary Length:** {summary_data.get('summary_length', 'medium')}\n\n")
            f.write("## Summary\n\n")
            f.write(summary_data.get('summary', ''))
            f.write("\n\n")
            f.write(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    else:  # text format
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Video: {summary_data.get('title', 'Unknown')}\n")
            f.write(f"Uploader: {summary_data.get('uploader', 'Unknown')}\n")
            f.write(f"Duration: {summary_data.get('duration_minutes', 0):.1f} minutes\n")
            f.write(f"Language: {summary_data.get('language', 'Unknown')}\n")
            f.write(f"Summary Length: {summary_data.get('summary_length', 'medium')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(summary_data.get('summary', ''))
            f.write(f"\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def display_summary_info(summary_data: Dict[str, Any]):
    """Display summary information in a nice format."""
    table = Table(title="Summary Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Title", summary_data.get('title', 'Unknown'))
    table.add_row("Uploader", summary_data.get('uploader', 'Unknown'))
    table.add_row("Duration", f"{summary_data.get('duration_minutes', 0):.1f} minutes")
    table.add_row("Language", summary_data.get('language', 'Unknown'))
    table.add_row("Summary Length", summary_data.get('summary_length', 'medium'))
    table.add_row("Word Count", str(summary_data.get('word_count', 0)))
    
    console.print(table)
    
    # Display summary in a panel
    summary_text = summary_data.get('summary', '')
    if summary_text:
        panel = Panel(summary_text, title="Generated Summary", border_style="green")
        console.print(panel)

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def estimate_processing_time(video_info: Dict[str, Any], whisper_model: str = "small") -> Dict[str, float]:
    """
    Estimate processing times for different stages.
    
    Args:
        video_info: Video information dictionary
        whisper_model: Whisper model size
        
    Returns:
        Dictionary with estimated times
    """
    duration_minutes = video_info.get('duration_minutes', 0)
    
    # Rough estimates based on M2 MacBook Air performance
    download_time = max(1, duration_minutes * 0.05)  # 5% of video duration
    
    transcription_times = {
        'tiny': duration_minutes * 0.1,
        'base': duration_minutes * 0.15,
        'small': duration_minutes * 0.2,
        'medium': duration_minutes * 0.4,
        'large': duration_minutes * 0.8
    }
    
    transcription_time = transcription_times.get(whisper_model, duration_minutes * 0.3)
    summarization_time = 0.5  # Usually under 1 minute
    
    return {
        'download': download_time,
        'transcription': transcription_time,
        'summarization': summarization_time,
        'total': download_time + transcription_time + summarization_time
    }

def cleanup_old_files(directory: str, max_age_hours: int = 24):
    """Clean up old temporary files."""
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for file_path in Path(directory).glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    console.print(f"[green]Cleaned up old file: {file_path.name}[/green]")
                except Exception as e:
                    console.print(f"[yellow]Could not clean up {file_path.name}: {e}[/yellow]")
