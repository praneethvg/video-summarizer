# Google Drive Setup Guide

This guide will help you set up Google Drive integration for automatic upload of transcripts and summaries.

## Prerequisites

- Google account with Google Drive access
- Python environment with the project dependencies installed

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

## Step 2: Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "YouTube Summarizer")
5. Download the JSON credentials file

## Step 3: Set Up Authentication

1. Place the downloaded credentials file in a secure location
2. Set the environment variable:
   ```bash
   export GOOGLE_CREDENTIALS_PATH="/path/to/your/credentials.json"
   ```
   
   Or add it to your `config.properties`:
   ```properties
   GOOGLE_CREDENTIALS_PATH=/path/to/your/credentials.json
   ```

## Step 4: Get Google Drive Folder ID

1. Open Google Drive in your browser
2. Navigate to the folder where you want to upload files
3. Copy the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```
4. Update `src/plugins/config.yaml`:
   ```yaml
   plugins:
     google_drive_uploader:
       folder_id: "FOLDER_ID_HERE"
   ```

## Step 5: First-Time Authentication

When you run the application for the first time with Google Drive enabled:

1. A browser window will open
2. Sign in with your Google account
3. Grant permissions to the application
4. The credentials will be saved for future use

## Configuration Options

### Plugin Configuration (`src/plugins/config.yaml`)

```yaml
plugins:
  google_drive_uploader:
    # Google Drive folder ID (required)
    folder_id: "your_folder_id_here"
    
    # Upload settings
    upload_transcripts: true    # Upload transcript files
    upload_summaries: true      # Upload summary files
    create_subfolders: true     # Create subfolders per video
```

### Environment Variables

```bash
# Google Drive credentials file path
export GOOGLE_CREDENTIALS_PATH="/path/to/credentials.json"

# Google Drive folder ID (alternative to plugin config)
export GOOGLE_DRIVE_FOLDER_ID="your_folder_id_here"
```

## File Organization

When `create_subfolders: true` is enabled, files are organized as follows:

```
Google Drive Folder/
├── Transcripts_VIDEO_ID/
│   └── video_transcript.txt
└── Summaries_VIDEO_ID/
    ├── video_summary.txt
    ├── video_summary.md
    └── video_summary.pdf
```

## Troubleshooting

### "Google Drive credentials not configured"
- Ensure `GOOGLE_CREDENTIALS_PATH` is set correctly
- Verify the credentials file exists and is readable
- Check that the credentials file is valid JSON

### "Google Drive folder ID not configured"
- Verify the folder ID in `src/plugins/config.yaml`
- Ensure the folder ID is correct (copy from Google Drive URL)
- Check that you have access to the folder

### "Permission denied" errors
- Ensure the Google account has access to the target folder
- Check that the OAuth scope includes Drive access
- Verify the credentials haven't expired

### "File upload failed"
- Check internet connection
- Verify the file exists locally before upload
- Ensure the Google Drive API is enabled in your project

## Security Notes

- Keep your credentials file secure and don't commit it to version control
- The credentials file contains sensitive information
- Consider using environment variables for production deployments
- Regularly rotate your OAuth credentials

## Testing the Setup

1. Run the application with a test video:
   ```bash
   python main.py --url "https://www.youtube.com/watch?v=TEST_VIDEO_ID"
   ```

2. Check the console output for Google Drive upload messages:
   ```
   ✅ Transcript uploaded to Google Drive: FILE_ID
   ✅ Summary uploaded to Google Drive: FILE_ID
   ```

3. Verify files appear in your Google Drive folder

## Advanced Configuration

### Custom File Naming

You can modify the Google Drive uploader plugin to customize file naming:

```python
# In src/plugins/google_drive_uploader.py
def _upload_file(self, file_path: str, folder_id: str) -> Optional[str]:
    # Customize file metadata here
    file_name = f"custom_prefix_{os.path.basename(file_path)}"
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    # ... rest of upload logic
```

### Multiple Upload Destinations

To upload to multiple Google Drive folders, create multiple instances of the uploader plugin or modify the existing one to support multiple folder IDs.

## Support

If you encounter issues:

1. Check the console output for specific error messages
2. Verify all configuration steps were completed
3. Test with a simple video first
4. Check Google Cloud Console for API usage and errors 