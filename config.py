import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials ---
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
OTCHARTS_KEY = os.environ["OTCHARTS_API_KEY"]

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
