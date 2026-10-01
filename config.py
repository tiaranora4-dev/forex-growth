import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = "Forex Growth"
BOT_USERNAME = "@ForexGrowthBot"

# Default currency pairs to track
DEFAULT_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]

# API endpoints (example: exchangerate.host — free, no key required)
FOREX_API_URL = "https://api.exchangerate.host/latest"
