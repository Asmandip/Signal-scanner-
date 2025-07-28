import aiohttp
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BITGET_TICKER_URL = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"

async def fetch_tickers(session):
    try:
        async with session.get(BITGET_TICKER_URL) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("data", [])
            else:
                logger.error(f"❌ Bitget ticker fetch failed: {resp.status}")
                return []
    except Exception as e:
        logger.error(f"❌ Error fetching tickers: {str(e)}")
        return []

async def scan_pair(session, symbol):
    INTERVAL = "1"
    LIMIT = 100
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity={INTERVAL}&limit={LIMIT}"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                logger.info(f"✅ Candles fetched for {symbol}")
            else:
                logger.warning(f"⚠️ Failed to fetch data for {symbol}: {resp.status}")
    except Exception as e:
        logger.error(f"❌ Exception for {symbol}: {str(e)}")

async def run_scanner():
    logger.info("📡 Scanner started...")
    async with aiohttp.ClientSession() as session:
        tickers = await fetch_tickers(session)
        if not tickers:
            return
        top_symbols = [t['symbol'] for t in tickers[:10]]
        tasks = [scan_pair(session, symbol) for symbol in top_symbols]
        await asyncio.gather(*tasks)