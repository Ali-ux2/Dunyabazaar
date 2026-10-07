import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID")
OTCHARTS_KEY = os.environ.get("OTCHARTS_API_KEY")

# --- Trading Settings (12 Pairs for Polling) ---
PAIRS = [
    "USDBRL_otc", "USDMXN_otc", "USDINR_otc", "USDPKR_otc",
    "USDDZD_otc", "USDARS_otc", "USDBDT_otc", "USDCOP_otc",
    "USDIDR_otc", "USDPHP_otc", "USDEGP_otc", "USDNGN_otc"
]

# --- S3 Strategy Parameters ---
SHORT_WINDOW = 10
LONG_WINDOW = 30
POLL_INTERVAL = 180  # 3 minutes in seconds
