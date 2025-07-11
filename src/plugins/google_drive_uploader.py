"""
Google Drive upload processor plugin.
Uploads transcript and summary files to Google Drive.
"""

import os
from pathlib import Path
from typing import List, Optional
from rich.console import Console

from src.plugins.base.plugin_base import ProcessorPlugin, PluginInfo
from src.events import TranscriptGeneratedEvent, SummaryCreatedEvent
from src.config import Config

console = Console()


class GoogleDriveUploader(ProcessorPlugin):
    """Google Drive upload processor plugin."""
    
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="google_drive_uploader",
            version="1.0.0",
            description="Uploads transcript and summary files to Google Drive",
            author="YouTube Summarizer Team",
            plugin_type="processor",
            entry_point="GoogleDriveUploader",
            config_schema={
                "folder_id": {"type": "string", "required": True, "description": "Google Drive folder ID"},
                "upload_transcripts": {"type": "boolean", "default": True},
                "upload_summaries": {"type": "boolean", "default": True},
                "create_subfolders": {"type": "boolean", "default": True}
            }
        )
    
    def get_event_types(self) -> List[type]:
        """Return the event types this processor handles."""
        return [TranscriptGeneratedEvent, SummaryCreatedEvent]
    
    def process_event(self, event) -> None:
        """Process events and upload files to Google Drive."""
        if isinstance(event, TranscriptGeneratedEvent):
            self._upload_transcript(event)
        elif isinstance(event, SummaryCreatedEvent):
            self._upload_summary(event)
    
    def _upload_transcript(self, event: TranscriptGeneratedEvent) -> None:
        """Upload transcript file to Google Drive."""
        if not self.config.get("upload_transcripts", True):
            return
        
        try:
            # For now, we'll save the transcript text to a file and then upload
            # In a real implementation, you might want to modify the transcription processor
            # to save the transcript to a file and include the path in the event
            
            # Create a temporary transcript file
            transcript_dir = Config.TEMP_DIR or "./temp"
            transcript_filename = f"{event.video_id}_transcript.txt"
            transcript_path = Path(transcript_dir) / transcript_filename
            
            # Save transcript text to file
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(event.transcript_text)
            
            # Upload to Google Drive
            folder_id = self.config.get("folder_id")
            if not folder_id:
                console.print("[red]❌ Google Drive folder ID not configured[/red]")
                return
            
            # Create subfolder if enabled
            if self.config.get("create_subfolders", True):
                folder_name = f"Transcripts_{event.video_id}"
                folder_id = self._create_or_get_folder(folder_name, folder_id)
            
            # Upload file
            file_id = self._upload_file(str(transcript_path), folder_id)
            if file_id:
                console.print(f"[green]✅ Transcript uploaded to Google Drive: {file_id}[/green]")
            else:
                console.print(f"[red]❌ Failed to upload transcript[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Error uploading transcript: {e}[/red]")
    
    def _upload_summary(self, event: SummaryCreatedEvent) -> None:
        """Upload summary file to Google Drive."""
        if not self.config.get("upload_summaries", True):
            return
        
        try:
            # Get summary file path
            summary_path = event.output_path
            if not summary_path or not os.path.exists(summary_path):
                console.print(f"[yellow]⚠️  Summary file not found: {summary_path}[/yellow]")
                return
            
            # Upload to Google Drive
            folder_id = self.config.get("folder_id")
            if not folder_id:
                console.print("[red]❌ Google Drive folder ID not configured[/red]")
                return
            
            # Create subfolder if enabled
            if self.config.get("create_subfolders", True):
                folder_name = f"Summaries_{event.video_id}"
                folder_id = self._create_or_get_folder(folder_name, folder_id)
            
            # Upload file
            file_id = self._upload_file(summary_path, folder_id)
            if file_id:
                console.print(f"[green]✅ Summary uploaded to Google Drive: {file_id}[/green]")
            else:
                console.print(f"[red]❌ Failed to upload summary[/red]")
                
        except Exception as e:
            console.print(f"[red]❌ Error uploading summary: {e}[/red]")
    
    def _create_or_get_folder(self, folder_name: str, parent_folder_id: str) -> str:
        """Create a folder in Google Drive or get existing one."""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            
            # Initialize Google Drive API
            creds = self._get_credentials()
            service = build('drive', 'v3', credentials=creds)
            
            # Check if folder already exists
            query = f"name='{folder_name}' and '{parent_folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            return folder.get('id')
            
        except Exception as e:
            console.print(f"[red]❌ Error creating folder: {e}[/red]")
            return parent_folder_id
    
    def _upload_file(self, file_path: str, folder_id: str) -> Optional[str]:
        """Upload a file to Google Drive."""
        try:
            from googleapiclient.discovery import build
            from google.oauth2.credentials import Credentials
            from googleapiclient.http import MediaFileUpload
            
            # Initialize Google Drive API
            creds = self._get_credentials()
            service = build('drive', 'v3', credentials=creds)
            
            # Prepare file metadata
            file_name = os.path.basename(file_path)
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            # Create media upload
            media = MediaFileUpload(file_path, resumable=True)
            
            # Upload file
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            console.print(f"[red]❌ Error uploading file: {e}[/red]")
            return None
    
    def _get_credentials(self):
        """Get Google Drive API credentials."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            # If you have a credentials file, load it
            creds_path = Config.GOOGLE_CREDENTIALS_PATH
            if creds_path and os.path.exists(creds_path):
                creds = Credentials.from_authorized_user_file(creds_path, ['https://www.googleapis.com/auth/drive'])
                
                # Refresh if expired
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                
                return creds
            
            # For now, return None - user needs to set up credentials
            console.print("[yellow]⚠️  Google Drive credentials not configured. Please set up authentication.[/yellow]")
            return None
            
        except Exception as e:
            console.print(f"[red]❌ Error loading Google Drive credentials: {e}[/red]")
            return None
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this processor supports."""
        return ['file_upload', 'google_drive_api', 'folder_management'] 