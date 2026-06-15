import logging
import sys

# Configure Logging for DevOps observability
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] | %(levelname)-8s | %(module)-12s | %(message)s',
    handlers=[
        logging.FileHandler("daily_digest.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Reconfigure stdout for Windows (utf-8)
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Brand Settings
BRAND_NAME = "Ahead of Everyone"
TAGLINE = "Innovating the Future, Today."
COPYRIGHT = "© 2026 Ahead of Everyone. All Rights Reserved."

import os

# OpenRouter / AI Settings
OPENROUTER_API_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free")  # Large, NVIDIA-backed primary model

# Color Palette (Luxury Slate & Neon Green)
COLOR_DARK = (10, 15, 29)        
COLOR_GRAY = (74, 85, 104)       
COLOR_LIGHT_GRAY = (247, 250, 252)  
COLOR_NEON = (34, 197, 94)       
COLOR_WHITE = (255, 255, 255)    

LOGO_PATH = "logo.svg"
FONTS_DIR = "assets"
