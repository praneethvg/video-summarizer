# YouTube Video Summarizer

An automated system that downloads videos from multiple platforms, transcribes them using Whisper, and generates AI-powered summaries. Built with a modern **event-driven architecture** and **plugin system** for maximum extensibility.

## 🏗️ Architecture

This project features a **modular, event-driven architecture** with a powerful plugin system:

### 🔌 **Plugin System**

The plugin system allows you to extend functionality without modifying core code:

- **Provider Plugins**: Add support for new video platforms (YouTube, Vimeo, etc.)
- **Processor Plugins**: Add new processing capabilities (sentiment analysis, Google Drive upload, etc.)
- **Dynamic Loading**: Plugins are discovered and loaded automatically
- **Configuration**: YAML-based plugin configuration

### 📁 **Project Structure**

```
youtube-summarizer/
├── src/
│   ├── downloaders/           # Multi-platform video downloaders
│   │   ├── base.py           # Abstract downloader interface
│   │   ├── youtube.py        # YouTube-specific downloader
│   │   ├── vimeo.py          # Vimeo-specific downloader
│   │   └── registry.py       # Downloader registry
│   ├── plugins/              # Plugin system
│   │   ├── base/             # Plugin base classes
│   │   ├── youtube_provider.py
│   │   ├── vimeo_provider.py
│   │   ├── sentiment_analyzer.py
│   │   ├── google_drive_uploader.py
│   │   └── config.yaml       # Plugin configuration
│   ├── processors/           # Core processing pipeline
│   ├── events/               # Event-driven architecture
│   ├── config.py             # Configuration management
│   ├── downloader.py         # Legacy interface (imports from downloaders/)
│   ├── plugin_manager.py     # Plugin management system
│   ├── transcriber.py        # Whisper transcription
│   ├── summarizer.py         # AI summarization
│   └── utils.py              # Utility functions
├── tests/                    # Unit tests
├── output/                   # Generated summaries
├── temp/                     # Temporary files
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Features

### **Core Features**
- **Multi-Platform Video Downloading**: Downloads videos from YouTube, Vimeo, and other platforms using yt-dlp
- **Smart Downloader Registry**: Automatically selects the appropriate downloader for each video platform
- **High-Quality Transcription**: Uses OpenAI's Whisper for accurate speech-to-text conversion
- **AI-Powered Summarization**: Generates intelligent summaries using OpenAI GPT models
- **M2 MacBook Optimization**: Leverages Metal GPU acceleration for faster processing
- **Progress Tracking**: Real-time progress updates during processing
- **Flexible Output**: Multiple output formats (text, markdown, JSON, PDF)
- **Batch Processing**: Process multiple videos in sequence

### **Advanced Features**
- **Event-Driven Architecture**: Modular, extensible processing pipeline
- **Plugin System**: Add new functionality without code changes
- **Provider Plugins**: Support for multiple video platforms (YouTube, Vimeo, etc.)
- **Processor Plugins**: Add custom processing capabilities (sentiment analysis, Google Drive upload, etc.)
- **Google Drive Integration**: Automatic upload of transcripts and summaries to Google Drive
- **Error Handling**: Robust error recovery and reporting
- **Configuration Management**: Flexible configuration system

## 📋 Requirements

- **macOS**: 10.15+ (Catalina or later)
- **Python**: 3.8 or higher
- **M2 MacBook Air/Pro**: Optimized for Apple Silicon
- **Internet Connection**: For video downloading and AI API calls
- **OpenAI API Key**: For summarization (get one at [OpenAI Platform](https://platform.openai.com/))
- **Google Drive API** (optional): For automatic file uploads

## 🛠️ Installation

### 1. Install System Dependencies
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg for audio processing
brew install ffmpeg
```

### 2. Set Up Python Environment
```bash
bash setup.sh
```

or

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Copy `config.properties.example` to `config.properties` in the project root.
2. Fill in your API keys and other settings in `config.properties`.
3. Do NOT commit `config.properties` to version control (it is in .gitignore).

### 4. Google Drive Setup (Optional)

To enable Google Drive uploads, see the detailed [Google Drive Setup Guide](GOOGLE_DRIVE_SETUP.md).

Quick setup:
1. Set up Google Drive API credentials
2. Add your Google Drive folder ID to `src/plugins/config.yaml`
3. Set the `GOOGLE_CREDENTIALS_PATH` environment variable

## 🎯 Usage

### **Basic Usage**
```bash
# Process a single video
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Process with custom output format
python main.py --url "https://www.youtube.com/watch?v=VIDEO_ID" --format markdown

# Process multiple videos
python main.py --urls "video1_url,video2_url,video3_url"

# Process Vimeo videos
python main.py --url "https://vimeo.com/VIDEO_ID"
```

### **Plugin Management**
```bash
# List available plugins
python main.py --list-plugins

# Show plugin status after processing
python main.py --url "VIDEO_URL" --show-plugins
```

### **Advanced Usage**

#### **Transcription Options**
```bash
# Use Whisper transcription (default)
python main.py --url "VIDEO_URL" --transcription-method whisper

# Use YouTube captions (faster, if available)
python main.py --url "VIDEO_URL" --transcription-method captions

# Custom Whisper model
python main.py --url "VIDEO_URL" --whisper-model medium
```

#### **Summarization Options**
```bash
# Different summary styles
python main.py --url "VIDEO_URL" --summary-style comprehensive
python main.py --url "VIDEO_URL" --summary-style bullet_points
python main.py --url "VIDEO_URL" --summary-style structured

# Different summary lengths
python main.py --url "VIDEO_URL" --summary-length short
python main.py --url "VIDEO_URL" --summary-length medium
python main.py --url "VIDEO_URL" --summary-length long

# Different output formats
python main.py --url "VIDEO_URL" --format text
python main.py --url "VIDEO_URL" --format markdown
python main.py --url "VIDEO_URL" --format json
python main.py --url "VIDEO_URL" --format pdf
```

## 🔌 Plugin System

### **How Downloads Work**

The system uses a **smart downloader registry** that automatically selects the appropriate downloader for each video platform:

1. **URL Detection**: When a video URL is provided, the system checks which platform it belongs to
2. **Downloader Selection**: The registry finds the appropriate downloader (YouTube, Vimeo, etc.)
3. **Video Processing**: The selected downloader handles video info extraction and audio downloading
4. **Plugin Integration**: Provider plugins work with the downloader registry to process videos

**Supported Platforms**:
- **YouTube**: Full support with video info, audio download, and captions
- **Vimeo**: Full support with video info, audio download, and captions
- **Extensible**: Easy to add support for new platforms via plugins

### **Available Plugins**

The system comes with built-in plugins:

- **`youtube_provider.py`**: Provider for YouTube videos
- **`vimeo_provider.py`**: Provider for Vimeo videos
- **`sentiment_analyzer.py`**: Sentiment analysis of transcripts and summaries
- **`google_drive_uploader.py`**: Uploads transcript and summary files to Google Drive

### **Creating Custom Downloaders**

To add support for a new video platform, create a custom downloader:

```python
# src/downloaders/custom_downloader.py
from src.downloaders import VideoDownloader
from typing import Dict, Any, Optional

class CustomDownloader(VideoDownloader):
    def can_handle_url(self, url: str) -> bool:
        # Check if this downloader can handle the URL
        return "customplatform.com" in url
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        # Extract video information
        # Implementation depends on the platform
        pass
    
    def download_audio(self, url: str, output_filename: Optional[str] = None) -> str:
        # Download audio from the video
        # Implementation depends on the platform
        pass
    
    def download_captions(self, url: str, output_filename: Optional[str] = None, 
                         lang: str = "en", prefer_manual: bool = True) -> Optional[str]:
        # Download captions if available
        pass
    
    def list_available_captions(self, url: str) -> Dict[str, Any]:
        # List available captions
        pass
```

Then register it in the downloader registry:

```python
from src.downloaders import DownloaderRegistry
from src.downloaders.custom_downloader import CustomDownloader

registry = DownloaderRegistry()
registry.register_downloader(CustomDownloader())
```

### **Creating Custom Plugins**

1. **Create a plugin file** in the `src/plugins/` directory:
```python
# src/plugins/my_plugin.py
from src.plugins.base.plugin_base import ProcessorPlugin, PluginInfo

class MyPlugin(ProcessorPlugin):
    def get_plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            plugin_type="processor",
            entry_point="MyPlugin"
        )
    
    def get_event_types(self):
        return [VideoDiscoveredEvent]  # Events to handle
    
    def process_event(self, event):
        # Your processing logic here
        pass
```

2. **Configure the plugin** in `src/plugins/config.yaml`:
```yaml
# Plugin-specific configurations
plugins:
  my_plugin:
    custom_setting: "value"

# List of enabled plugins (empty list = enable all discovered plugins)
enabled_plugins:
  - youtube_provider
  - vimeo_provider
  - sentiment_analyzer
  - google_drive_uploader
  - my_plugin

# Load all discovered plugins by default
load_all_plugins_by_default: true
```

3. **Use the plugin**:
```bash
python main.py --url "VIDEO_URL"
```

### **Plugin Configuration Options**

The plugin system supports flexible configuration:

- **`enabled_plugins`**: List of plugins to enable (empty = enable all)
- **`load_all_plugins_by_default`**: Load all discovered plugins by default
- **Individual plugin configs**: Plugin-specific settings

**Configuration Examples**:

```yaml
# Enable all plugins by default
enabled_plugins: []

# Enable specific plugins only
enabled_plugins:
  - youtube_provider
  - sentiment_analyzer

# Plugin-specific configuration
plugins:
  google_drive_uploader:
    folder_id: "your_google_drive_folder_id"
    upload_transcripts: true
    upload_summaries: true
    create_subfolders: true
  
  sentiment_analyzer:
    analysis_type: "detailed"
    confidence_threshold: 0.8
```

## 🔄 Processing Pipeline

The system follows this event-driven pipeline:

1. **Video Discovery**: Provider plugins detect and process video URLs
2. **Download**: Smart downloader registry selects appropriate downloader
3. **Transcription**: Whisper or captions generate transcript
4. **Summarization**: AI generates summary in various formats
5. **Post-Processing**: Processor plugins handle additional tasks:
   - Sentiment analysis
   - Google Drive uploads
   - Custom processing

## 🧪 Testing



### **Run Unit Tests**
```bash
python -m pytest tests/
```

## 📊 Performance

- **M2 MacBook Optimization**: Leverages Metal GPU for faster Whisper processing
- **Parallel Processing**: Multiple videos can be processed simultaneously
- **Caching**: Temporary files are managed efficiently
- **Progress Tracking**: Real-time updates during long operations

## 🤝 Contributing

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed development setup and contribution guidelines.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### **Common Issues**

**Import errors?**
- Verify virtual environment is activated
- Check that `src/` and `src/plugins/` are in your Python path
- The `pyrightconfig.json` should handle this automatically

**Google Drive uploads not working?**
- Ensure Google Drive API credentials are properly configured
- Check that the folder ID in `src/plugins/config.yaml` is correct
- Verify the `GOOGLE_CREDENTIALS_PATH` environment variable is set

**Plugin not loading?**
- Check the plugin is listed in `enabled_plugins` in `src/plugins/config.yaml`
- Verify the plugin file follows the correct format
- Check plugin logs for specific error messages

**Video download issues?**
- Ensure ffmpeg is installed: `brew install ffmpeg`
- Check internet connection
- Verify the video URL is accessible

### **Getting Help**

1. Check the [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions
2. Review the plugin configuration in `src/plugins/config.yaml`
3. Run `python main.py --list-plugins` to verify plugin loading
4. Check the output directory for generated files

## 🎉 What's New

- **Multi-platform support**: YouTube and Vimeo with extensible downloader system
- **Plugin architecture**: Clean, modular system for easy extension
- **Google Drive integration**: Automatic upload of transcripts and summaries
- **Event-driven processing**: Robust pipeline with error handling
- **Smart downloader registry**: Automatic platform detection and handling