import aiohttp
import asyncio
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("scanner")

HEADERS = {
    'Content-Type': 'application/json'
}

BASE_URL = "https://api.bitget.com"

async def fetch_tickers(session):
    url = f"{BASE_URL}/api/v2/mix/market/tickers?productType=umcbl"
    try:
        async with session.get(url, headers=HEADERS) as resp:
            if resp.status != 200:
                logger.error(f"❌ Bitget ticker fetch failed: {resp.status}")
                return None
            data = await resp.json()
            return data.get("data", [])
    except Exception as e:
        logger.error(f"❌ Exception while fetching tickers: {e}")
        return None

async def run_scanner():
    logger.info("📡 Scanner started...")
    async with aiohttp.ClientSession() as session:
        while True:
            tickers = await fetch_tickers(session)
            if tickers:
                logger.info(f"✅ Tickers fetched: {len(tickers)} coins")
            await asyncio.sleep(60)