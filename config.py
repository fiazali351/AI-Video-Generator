"""
config.py - API Keys & Global Settings
"""

import os

# API KEYS
OPENAI_API_KEY     = os.getenv("OPENAI_API_KEY",     "YOUR_GROQ_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "not_used")
PEXELS_API_KEY     = os.getenv("PEXELS_API_KEY",     "not_used")
SERPER_API_KEY     = "YOUR_SERPER_KEY"
VIDEO_WIDTH  = 1280
VIDEO_HEIGHT = 720
VIDEO_FPS     = 30
VIDEO_FORMAT  = "mp4"

# SUBTITLE SETTINGS
SUBTITLE_FONT      = "Arial"
SUBTITLE_FONTSIZE  = 48
SUBTITLE_COLOR     = "white"
SUBTITLE_BG_COLOR  = "black"
SUBTITLE_POSITION  = ("center", 0.85)

# OPENAI SETTINGS
OPENAI_MODEL    = "llama-3.3-70b-versatile"
SCRIPT_SECTIONS = 6

# ELEVENLABS SETTINGS
DEFAULT_VOICE = "Rachel"
TTS_MODEL     = "eleven_multilingual_v2"

# PEXELS SETTINGS
PREFERRED_MEDIA           = "video"
PEXELS_VIDEO_MIN_DURATION = 5
