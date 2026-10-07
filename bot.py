import asyncio
import logging
from datetime import datetime, timedelta
from config import BOT_TOKEN, CHANNEL_ID, OTCHARTS_KEY, PAIRS, MTG_MAX_STEPS
from analyzer import S3Analyzer
from otcharts import Client, QuotaExceeded
from telegram import Bot
from telegram.error import TelegramError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

otc = Client(api_key=OTCHARTS_KEY)
bot = Bot(token=BOT_TOKEN)
analyzer = S3Analyzer()

# Global state to track active trades
active_trades = {}

async def send_message(text: str):
    try:
        await bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode="Markdown")
        logger.info(f"Sent: {text.splitlines()[0]}")
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")

async def run_sniper_loop():
    logger.info("Starting DunyaBazaar Sniper M5 Bot (12 Pairs, Silent MTG)...")
    
    # Warm up analyzer
    for pair in PAIRS:
        try:
            bars = otc.candles("quotex", pair, tf=300, limit=50) # tf=300 is 5 minutes
            for bar in bars:
                analyzer.analyze(pair, bar.close)
        except Exception as e:
            logger.error(f"Warmup failed for {pair}: {e}")

    logger.info("Warmup complete. Entering precise M5 loop.")

    while True:
        now = datetime.now()
        seconds = now.second
        minutes_mod_5 = now.minute % 5

        # --- PHASE 1: SEND INITIAL SIGNAL (At :52 seconds of the 4th minute) ---
        # e.g., 10:59:52 for an 11:00:00 entry
        if minutes_mod_5 == 4 and seconds == 52:
            logger.info(f"Scanning for M5 signals at {now.strftime('%H:%M:%S')}...")
            for pair in PAIRS:
                try:
                    bars = otc.candles("quotex", pair, tf=300, limit=2)
                    if not bars: continue
                    
                    latest_price = bars[-1].close
                    direction, strength = analyzer.analyze(pair, latest_price)
                    
                    if direction and pair not in active_trades and analyzer.last_signal.get(pair) != direction:
                        active_trades[pair] = {
                            'direction': direction,
                            'entry_price': latest_price,
                            'step': 1
                        }
                        analyzer.last_signal[pair] = direction
                        
                        arrow = "🟢" if direction == "CALL" else "🔴"
                        # Entry time is 8 seconds from now (the next 5-minute mark)
                        entry_time = (now + timedelta(seconds=8)).strftime("%H:%M")
                        
                        text = (
                            f"🚀 *Signal ready: {pair.upper().replace('_OTC', '')}*\n"
                            f"Direction: {arrow} *{direction}*\n"
                            f"Timeframe: *M5*\n"
                            f"Entry Time: `{entry_time}`\n"
                            f"Price: `{latest_price:.5f}`\n"
                            f"Strength: `{strength*100:.2f}%`\n"
                            f"⚙️ *MTG Plan:* Step 1. If loss, double amount at {entry_time[0:3]}:00 and follow the *same direction*.\n"
                            f"—\n"
                            f"🌍 DunyaBazaar"
                        )
                        await send_message(text)
                        await asyncio.sleep(8) # 8-second delay between pairs
                except Exception as e:
                    logger.error(f"Error scanning {pair}: {e}")

        # --- PHASE 2: EVALUATE OUTCOME (At :01 seconds of the 5th minute) ---
        # e.g., 11:05:01 for a trade that expired at 11:05:00
        elif minutes_mod_5 == 0 and seconds == 1:
            logger.info(f"Checking M5 results at {now.strftime('%H:%M:%S')}...")
            for pair in list(active_trades.keys()):
                try:
                    trade = active_trades[pair]
                    bars = otc.candles("quotex", pair, tf=300, limit=1)
                    if not bars: continue
                    
                    close_price = bars[-1].close
                    direction = trade['direction']
                    entry_price = trade['entry_price']
                    step = trade['step']

                    is_win = (direction == 'CALL' and close_price > entry_price) or \
                             (direction == 'PUT' and close_price < entry_price)

                    if is_win:
                        if step == 1:
                            text = f"✅ *{pair.upper().replace('_OTC', '')}*\nResult: *WIN*\nCycle closed."
                        else:
                            text = f"✅ *{pair.upper().replace('_OTC', '')}*\nResult: *WIN BY MTG*\nCycle closed."
                        await send_message(text)
                        del active_trades[pair]
                    
                    else: # LOSS
                        if step < MTG_MAX_STEPS:
                            # Silent MTG Step: Update state, do NOT send a message
                            logger.info(f"Loss on {pair} Step {step}. Silently moving to Step {step+1}.")
                            trade['step'] += 1
                            trade['entry_price'] = close_price
                        else:
                            # Max MTG reached, cycle is OVER - Send final result
                            text = f"❌ *{pair.upper().replace('_OTC', '')}*\nResult: *LOSS* (Max MTG Reached)\nCycle closed."
                            await send_message(text)
                            del active_trades[pair]
                            
                except Exception as e:
                    logger.error(f"Error evaluating {pair}: {e}")

        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(run_sniper_loop())
