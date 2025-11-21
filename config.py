"""
Configuration file for Kleinanzeigen Hunter
"""

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
