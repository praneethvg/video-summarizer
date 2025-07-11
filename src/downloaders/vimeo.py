"""
Vimeo-specific video downloader using yt-dlp.
"""

import re
from typing import Optional, Dict, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .base import VideoDownloader

console = Console()

class VimeoDownloader(VideoDownloader):
    """Vimeo-specific video downloader using yt-dlp."""
    
    def can_handle_url(self, url: str) -> bool:
        """Check if this is a Vimeo URL."""
        vimeo_patterns = [
            r'(?:vimeo\.com/\d+)',
            r'(?:vimeo\.com/channels/\w+/\d+)',
            r'(?:vimeo\.com/groups/\w+/videos/\d+)'
        ]
        return any(re.search(pattern, url) for pattern in vimeo_patterns)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Get video information without downloading."""
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise Exception("Could not extract video info")
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', '')[:200] + '...' if info.get('description') else ''
                }
            except Exception as e:
                console.print(f"[red]Error getting video info: {e}[/red]")
                raise
    
    def download_audio(self, url: str, output_filename: Optional[str] = None) -> str:
        """
        Download audio from Vimeo video.
        
        Args:
            url: Vimeo video URL
            output_filename: Optional custom filename
            
        Returns:
            Path to downloaded audio file
        """
        import yt_dlp
        
        if not output_filename:
            # Generate filename from video info
            info = self.get_video_info(url)
            safe_title = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_filename = f"{safe_title[:50]}.mp3"
        
        output_path = self.temp_dir / output_filename
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': str(output_path.with_suffix('')),
            'quiet': True,
            'no_warnings': True,
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Downloading audio...", total=None)
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                progress.update(task, description="✅ Audio downloaded successfully!")
                return str(output_path)
                
            except Exception as e:
                progress.update(task, description=f"❌ Download failed: {e}")
                raise
    
    def download_captions(self, url: str, output_filename: Optional[str] = None, lang: str = "en", prefer_manual: bool = True) -> Optional[str]:
        """
        Download closed captions from Vimeo video.
        Args:
            url: Vimeo video URL
            output_filename: Optional custom filename
            lang: Language code for captions (default: 'en')
            prefer_manual: Whether to prefer manual captions over auto-generated (default: True)
        Returns:
            Path to downloaded captions file, or None if not available
        """
        import yt_dlp
        
        info = self.get_video_info(url)
        safe_title = "".join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').replace('-', '_')
        safe_title = "".join(c for c in safe_title if c.isalnum() or c == '_')
        output_filename = output_filename or f"{safe_title[:50]}_{lang}_captions"
        output_path = self.temp_dir / f"{output_filename}.{lang}.srt"

        console.print(f"[blue]Attempting to download captions to: {output_path}[/blue]")

        # Try to download captions
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [lang],
            'subtitlesformat': 'srt',
            'outtmpl': str(self.temp_dir / output_filename),
            'quiet': False,
            'no_warnings': False,
        }

        console.print(f"[yellow]Trying to download captions for language: {lang}[/yellow]")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                if output_path.exists():
                    console.print(f"[green]✅ Downloaded captions for language: {lang}[/green]")
                    console.print(f"[green]File size: {output_path.stat().st_size} bytes[/green]")
                    return str(output_path)
                else:
                    console.print(f"[red]❌ File not found after download: {output_path}[/red]")
                    console.print(f"[blue]Files in temp directory: {list(self.temp_dir.glob('*'))}[/blue]")
            except Exception as e:
                console.print(f"[yellow]No captions found for {lang}: {e}[/yellow]")

        return None
    
    def list_available_captions(self, url: str) -> Dict[str, Any]:
        """
        List available captions for a Vimeo video.
        Args:
            url: Vimeo video URL
        Returns:
            Dictionary with available captions information
        """
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise Exception("Could not extract video info")
                captions = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                return {
                    'manual_captions': captions,
                    'auto_captions': auto_captions,
                    'all_languages': list(set(list(captions.keys()) + list(auto_captions.keys())))
                }
            except Exception as e:
                console.print(f"[red]Error getting captions info: {e}[/red]")
                return {'manual_captions': {}, 'auto_captions': {}, 'all_languages': []} 