# scanner.py

import aiohttp
import logging

async def fetch_tickers():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=USDT-FUTURES"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    logging.error(f"❌ Ticker fetch failed: {resp.status} — {text}")
                    return []
                data = await resp.json()
                return data.get("data", [])
    except Exception as e:
        logging.error(f"❌ Exception in fetch_tickers: {e}")
        return []

async def run_scanner():
    logging.info("🔍 Running Bitget scanner...")
    tickers = await fetch_tickers()
    logging.info(f"✅ Tickers fetched: {len(tickers)} symbols")
    # You can add logic here to filter/sort or scan based on RSI, etc.