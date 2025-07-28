import aiohttp
import asyncio
import logging

from utils.telegram import send_telegram_message  # নিশ্চিত করুন এই ফাইল ও ফাংশন ঠিক আছে

# ✅ Bitget API থেকে মার্কেট ডেটা আনা
async def fetch_symbols():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                print(f"🔄 Bitget API Status: {resp.status}")
                text = await resp.text()
                print(f"📥 Bitget API Response: {text[:500]}")  # বড় response কাটছাঁট করে দেখানো
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.error(f"❌ Failed to fetch symbols: HTTP {resp.status}")
                    return None
        except Exception as e:
            logging.error(f"❌ Exception during fetch_symbols: {e}")
            return None

# ✅ মূল স্ক্যানার ফাংশন
async def run_scanner():
    data = await fetch_symbols()
    if data is None or "data" not in data:
        logging.error("❌ Symbol data fetch failed or 'data' key missing in response.")
        return

    try:
        all_symbols = [x["symbol"] for x in data["data"]]
        print(f"✅ Total symbols fetched: {len(all_symbols)}")

        # ✅ এখানে ট্রেডিং লজিক বসবে — এখন শুধু ডেমো প্রিন্ট এবং টেলিগ্রাম বার্তা পাঠানো হচ্ছে
        for symbol in all_symbols[:5]:  # শুধু প্রথম ৫টা সিম্বল
            print(f"🔍 Scanning {symbol}")
            await send_telegram_message(f"🟢 Scanned symbol: {symbol}")

    except Exception as e:
        logging.error(f"❌ Exception in run_scanner: {e}")