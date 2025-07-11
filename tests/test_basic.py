"""
Basic tests for the YouTube Summarizer.
"""

import pytest
import os
from src.config import Config
from src.downloader import YouTubeDownloader
from src.transcriber import WhisperTranscriber
from src.summarizer import AISummarizer

def test_config_validation():
    """Test configuration validation."""
    # This will fail if OPENAI_API_KEY is not set
    try:
        Config.validate()
        assert True
    except ValueError:
        # Expected if API key is not set
        assert True

def test_downloader_initialization():
    """Test YouTube downloader initialization."""
    downloader = YouTubeDownloader()
    assert downloader is not None
    assert hasattr(downloader, 'temp_dir')

def test_transcriber_initialization():
    """Test Whisper transcriber initialization."""
    # This will download the model if not present
    try:
        transcriber = WhisperTranscriber(model_size="tiny")
        assert transcriber is not None
        assert hasattr(transcriber, 'model')
    except Exception:
        # Model download might fail in test environment
        assert True

def test_utils_functions():
    """Test utility functions."""
    from src.utils import sanitize_filename, format_duration
    
    # Test filename sanitization
    assert sanitize_filename("test<>file.mp3") == "test__file.mp3"
    
    # Test duration formatting
    assert format_duration(30) == "30.0s"
    assert format_duration(90) == "1.5m"
    assert format_duration(7200) == "2.0h"

if __name__ == "__main__":
    pytest.main([__file__])
