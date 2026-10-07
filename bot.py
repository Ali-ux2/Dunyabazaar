import os
import asyncio
import logging
from collections import deque
from dotenv import load_dotenv
from otcharts import Client, QuotaExceeded, TooManyStreams, HouseBusy, PlanError
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

# --- Configuration ---
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL_ID = os.environ["TELEGRAM_CHANNEL_ID"]
OTCHARTS_KEY = os.environ["OTCHARTS_API_KEY"]

# Your 12 pairs (Quotex book uses underscore format)
PAIRS = [
    "EURUSD_otc", "GBPUSD_otc", "USDJPY_otc", "AUDUSD_otc",
    "USDCAD_otc", "USDCHF_otc", "NZDUSD_otc", "EURGBP_otc",
    "EURJPY_otc", "GBPJPY_otc", "AUDJPY_otc", "EURAUD_otc"
]

# Strategy parameters (S3 = Simple Moving Average Crossover)
SHORT_WINDOW = 10
LONG_WINDOW = 30
PRICE_HISTORY = {pair: deque(maxlen=LONG_WINDOW) for pair in PAIRS}
LAST_SIGNAL = {pair: None for pair in PAIRS}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

otc = Client(api_key=OTCHARTS_KEY)
bot = Bot(token=BOT_TOKEN)


def analyze_s3(pair: str, price: float) -> str | None:
    """
    S3 Strategy: Simple Moving Average Crossover.
    Returns 'CALL' if short MA crosses above long MA,
    'PUT' if short MA crosses below long MA,
    or None if no crossover occurs.
    """
    history = PRICE_HISTORY[pair]
    history.append(price)

    if len(history) < LONG_WINDOW:
        return None  # Not enough data yet

    short_ma = sum(list(history)[-SHORT_WINDOW:]) / SHORT_WINDOW
    long_ma = sum(history) / LONG_WINDOW

    prev_short = sum(list(history)[-SHORT_WINDOW-1:-1]) / SHORT_WINDOW if len(history) > SHORT_WINDOW else short_ma
    prev_long = sum(list(history)[-LONG_WINDOW-1:-1]) / LONG_WINDOW if len(history) > LONG_WINDOW else long_ma

    # Detect crossover
    if prev_short <= prev_long and short_ma > long_ma:
        return "CALL"
    elif prev_short >= prev_long and short_ma < long_ma:
        return "PUT"
    return None


async def send_signal(pair: str, price: float, direction: str):
    """Send a formatted signal to the Telegram channel."""
    arrow = "🟢" if direction == "CALL" else "🔴"
    text = (
        f"{arrow} *{pair.upper().replace('_OTC', '')}*\n"
        f"Direction: *{direction}*\n"
        f"Price: `{price:.5f}`\n"
        f"Strategy: S3 (MA Crossover)\n"
        f"—\n"
        f"🌍 DunyaBazaar — One world. One market."
    )
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        logger.info(f"Signal sent: {pair} {direction} @ {price}")
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")


async def main():
    logger.info("Starting DunyaBazaar bot with S3 analyzer...")
    logger.info(f"Tracking {len(PAIRS)} pairs: {', '.join(PAIRS)}")

    try:
        for tick in otc.stream("quotex", PAIRS):
            direction = analyze_s3(tick.symbol, tick.price)
            if direction and LAST_SIGNAL[tick.symbol] != direction:
                LAST_SIGNAL[tick.symbol] = direction
                await send_signal(tick.symbol, tick.price, direction)

    except QuotaExceeded:
        logger.error("Daily request quota spent. Wait until midnight UTC.")
    except TooManyStreams:
        logger.error("Stream limit reached. API Lite allows only 1 stream.")
    except HouseBusy as e:
        logger.warning(f"Venue busy. Retry after {e.retry_after}s.")
    except PlanError:
        logger.error("This book is not included in your plan.")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
