"""
Configuration settings for the YouTube Summarizer.
Optimized for M2 MacBook Air performance.
"""

import os
import configparser

class Config:
    """Configuration class for the YouTube Summarizer."""
    _loaded = False
    _config = None

    # Config values (set after load)
    OPENAI_API_KEY = None
    OPENAI_MODEL = None
    DEFAULT_WHISPER_MODEL = None
    WHISPER_DEVICE = None
    WHISPER_COMPUTE_TYPE = None
    WHISPER_BATCH_SIZE = None
    DEFAULT_SUMMARY_LENGTH = None
    OUTPUT_DIR = None
    TEMP_DIR = None
    # Google Drive API
    GOOGLE_CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', None)

    # Static options
    VIDEO_QUALITY = 'bestaudio'
    AUDIO_FORMAT = 'mp3'
    SUMMARY_LENGTHS = {
        'short': 150,
        'medium': 300,
        'long': 500
    }
    WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large']
    OUTPUT_FORMATS = ['text', 'markdown', 'json']

    @classmethod
    def load(cls, path='config.properties'):
        config = configparser.ConfigParser()
        config.read(path)
        section = config['DEFAULT']
        cls._config = config
        cls.OPENAI_API_KEY = section.get('OPENAI_API_KEY')
        cls.OPENAI_MODEL = section.get('OPENAI_MODEL', 'gpt-4o')
        cls.DEFAULT_WHISPER_MODEL = section.get('DEFAULT_WHISPER_MODEL', 'small')
        cls.WHISPER_DEVICE = section.get('WHISPER_DEVICE', 'auto')
        cls.WHISPER_COMPUTE_TYPE = section.get('WHISPER_COMPUTE_TYPE', 'float16')
        cls.WHISPER_BATCH_SIZE = int(section.get('WHISPER_BATCH_SIZE', '16'))
        cls.DEFAULT_SUMMARY_LENGTH = section.get('DEFAULT_SUMMARY_LENGTH', 'medium')
        cls.OUTPUT_DIR = section.get('OUTPUT_DIR', './output')
        cls.TEMP_DIR = section.get('TEMP_DIR', './temp')
        cls._loaded = True

    @classmethod
    def validate(cls):
        if not cls._loaded:
            raise RuntimeError("Config not loaded. Call Config.load() before use.")
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in config.properties")
        if cls.DEFAULT_WHISPER_MODEL not in cls.WHISPER_MODELS:
            raise ValueError(f"Invalid Whisper model: {cls.DEFAULT_WHISPER_MODEL}")
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        return True
