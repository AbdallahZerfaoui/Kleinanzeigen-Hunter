"""Configuration file for Kleinanzeigen Hunter."""

from __future__ import annotations

import os

# Base URLs
KLEINANZEIGEN_BASE_URL = "https://www.kleinanzeigen.de"
INSERAT_URL_TEMPLATE = f"{KLEINANZEIGEN_BASE_URL}/s-anzeige/{{id}}"

# Browser settings
BROWSER_HEADLESS = True
BROWSER_TIMEOUT = 30000  # milliseconds
BROWSER_VIEWPORT = {"width": 1920, "height": 1080}

# Scraping settings
MAX_RETRIES = 3
REQUEST_DELAY = 1  # seconds between requests

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Cache/Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "false").strip().lower() in {"1", "true", "yes"}
