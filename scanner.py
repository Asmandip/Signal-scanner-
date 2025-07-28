import aiohttp
import asyncio
import logging

from utils.telegram import send_telegram_message

# ✅ মার্কেট ডেটা ফেচ (USDT-M Futures)
async def fetch_symbols():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
    headers = {
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                print(f"🔄 Bitget API Status: {resp.status}")
                text = await resp.text()
                print(f"📥 Bitget API Response (first 500 chars):\n{text[:500]}")
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.error(f"❌ Failed to fetch symbols: HTTP {resp.status}")
                    await send_telegram_message(f"❌ Bitget API error: HTTP {resp.status}")
                    return None
        except Exception as e:
            logging.error(f"❌ Exception during fetch_symbols: {e}")
            await send_telegram_message(f"❌ Bitget API exception: {e}")
            return None

# ✅ স্ক্যানার বডি
async def run_scanner():
    data = await fetch_symbols()
    if data is None or "data" not in data:
        logging.error("❌ Symbol data fetch failed or 'data' key missing.")
        return

    try:
        all_symbols = [x["symbol"] for x in data["data"]]
        print(f"✅ Total symbols fetched: {len(all_symbols)}")

        # ট্রেডিং লজিকের ডেমো
        for symbol in all_symbols[:5]:  # প্রথম ৫টা সিম্বল
            print(f"🔍 Scanning {symbol}")
            await send_telegram_message(f"🟢 Scanned: {symbol}")

    except Exception as e:
        logging.error(f"❌ Exception in run_scanner: {e}")