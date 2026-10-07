# DunyaBazaar OTC Signals Bot

Automated trading signal bot for the DunyaBazaar Telegram channel. It connects to OTCharts to track live Quotex data across 12 currency pairs and uses the S3 (Simple Moving Average Crossover) strategy to generate CALL/PUT signals.

## Architecture
- **OTCharts API Lite:** Fetches live tick data.
- **S3 Analyzer:** Detects moving average crossovers.
- **Telegram Bot:** Posts formatted signals to the channel.
- **Railway:** Hosts the bot 24/7.

## Files
- `config.py` — Environment variables and trading settings.
- `analyzer.py` — The S3 trading strategy logic.
- `bot.py` — Main application loop and Telegram integration.
- `requirements.txt` — Python dependencies.
- `Procfile` — Railway start command.

## Environment Variables (Railway)
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`
- `OTCHARTS_API_KEY`

## Disclaimer
This bot is for educational purposes only. It does not place trades. Trading involves significant risk.
