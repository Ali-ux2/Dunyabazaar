import os
from dotenv import load_dotenv

load_dotenv()

# --- Credentials ---
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
OTCHARTS_KEY = os.environ["OTCHARTS_API_KEY"]

# --- Trading Settings ---
PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc",
    "USDCAD_otc", "USDCHF_otc", "NZDUSD_otc", "EURGBP_otc",
    "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc", "EURAUD_otc"
]

# --- S3 Strategy Parameters ---
SHORT_WINDOW = 10
LONG_WINDOW = 30
