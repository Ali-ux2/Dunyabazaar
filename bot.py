import asyncio
import logging
from config import BOT_TOKEN, CHANNEL_ID, OTCHARTS_KEY, PAIRS
from analyzer import S3Analyzer
from otcharts import Client, QuotaExceeded, TooManyStreams, HouseBusy, PlanError
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

otc = Client(api_key=OTCHARTS_KEY)
bot = Bot(token=BOT_TOKEN)
analyzer = S3Analyzer()

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
    logger.info(f"Tracking {len(PAIRS)} pairs.")

    try:
        for tick in otc.stream("quotex", PAIRS):
            direction = analyzer.analyze(tick.symbol, tick.price)
            
            # Only send a signal if the direction changed
            if direction and analyzer.last_signal[tick.symbol] != direction:
                analyzer.last_signal[tick.symbol] = direction
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
