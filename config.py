import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials (Read from Railway Variables) ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
OTCHARTS_KEY = os.environ.get("OTCHARTS_API_KEY")

# --- Trading Settings (5 Pairs for Lite Plan) ---
PAIRS = [
    "USDBRL_otc",
    "USDMXN_otc",
    "USDINR_otc",
    "USDPKR_otc",
    "USDARS_otc"
]

# --- S3 Strategy Parameters ---
SHORT_WINDOW = 10
LONG_WINDOW = 30
