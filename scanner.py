import os
import asyncio
import aiohttp
import logging
from dotenv import load_dotenv
from utils import analyze_data, send_telegram_signal, fetch_klines

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(level=logging.INFO)

HEADERS = {
    'Content-Type': 'application/json'
}
SYMBOLS_URL = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"

async def fetch_symbols(session):
    async with session.get(SYMBOLS_URL) as res:
        if res.status != 200:
            logging.error(f"❌ Bitget ticker fetch failed: {res.status}")
            return []
        data = await res.json()
        return [item["symbol"] for item in data.get("data", [])]

async def scan_market():
    async with aiohttp.ClientSession() as session:
        symbols = await fetch_symbols(session)
        tasks = [scan_symbol(session, symbol) for symbol in symbols]
        await asyncio.gather(*tasks)

async def scan_symbol(session, symbol):
    try:
        klines = await fetch_klines(session, symbol, "3m", 100)
        if not klines:
            return
        signal = analyze_data(klines)
        if signal:
            await send_telegram_signal(symbol, signal)
    except Exception as e:
        logging.error(f"Error scanning {symbol}: {e}")

def run_scanner():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scan_market())