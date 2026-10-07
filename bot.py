import asyncio
import logging
from config import BOT_TOKEN, CHANNEL_ID, OTCHARTS_KEY, PAIRS, POLL_INTERVAL
from analyzer import S3Analyzer
from otcharts import Client, QuotaExceeded, PlanError
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

otc = Client(api_key=OTCHARTS_KEY)
bot = Bot(token=BOT_TOKEN)
analyzer = S3Analyzer()

async def send_signal(pair: str, price: float, direction: str, strength: float):
    arrow = "🟢" if direction == "CALL" else "🔴"
    text = (
        f"{arrow} *{pair.upper().replace('_OTC', '')}*\n"
        f"Direction: *{direction}*\n"
        f"Price: `{price:.5f}`\n"
        f"Strength: `{strength*100:.2f}%`\n"
        f"—\n"
        f"🌍 DunyaBazaar — One world. One market."
    )
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        logger.info(f"Signal sent: {pair} {direction} @ {price}")
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")

async def warm_up():
    """Fetch historical candles to populate the analyzer on startup."""
    logger.info("Warming up analyzer with historical data...")
    for pair in PAIRS:
        try:
            bars = otc.candles("quotex", pair, tf=60, limit=50)
            for bar in bars:
                analyzer.analyze(pair, bar.close)
            logger.info(f"Warmed up {pair}: {len(bars)} candles")
        except Exception as e:
            logger.error(f"Warm-up failed for {pair}: {e}")
        await asyncio.sleep(1)  # Small delay to avoid rate limits

async def main():
    logger.info("Starting DunyaBazaar bot (Polling 12 pairs, Best Signal every 3 mins)...")
    
    # 1. Warm up the analyzer first
    await warm_up()
    logger.info("Warm-up complete. Starting poll loop.")

    # 2. Main Polling Loop
    while True:
        try:
            best_pair = None
            best_price = None
            best_direction = None
            best_strength = -1.0

            # Poll all 12 pairs
            for pair in PAIRS:
                try:
                    # Fetch the latest 2 candles (1 request per pair)
                    bars = otc.candles("quotex", pair, tf=60, limit=2)
                    if bars:
                        latest_price = bars[-1].close
                        direction, strength = analyzer.analyze(pair, latest_price)
                        
                        # Only consider signals that haven't been sent recently
                        if direction and analyzer.last_signal.get(pair) != direction:
                            if strength > best_strength:
                                best_strength = strength
                                best_pair = pair
                                best_price = latest_price
                                best_direction = direction
                except Exception as e:
                    logger.error(f"Error polling {pair}: {e}")

            # 3. Send the best signal found in this cycle
            if best_pair:
                analyzer.last_signal[best_pair] = best_direction
                await send_signal(best_pair, best_price, best_direction, best_strength)
            else:
                logger.info("No valid crossovers found in this cycle.")

        except QuotaExceeded:
            logger.error("Daily request quota spent. Wait until midnight UTC.")
        except PlanError:
            logger.error("Plan error: Ensure Quotex is your selected book.")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")

        # Wait 3 minutes before the next cycle
        await asyncio.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
