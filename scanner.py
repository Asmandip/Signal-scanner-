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
                print(f"\n📥 FULL RESPONSE TEXT:\n{text}\n")  # 👉 এটা দেখতেই হবে
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.error(f"❌ Failed to fetch symbols: HTTP {resp.status}")
                    return None
        except Exception as e:
            logging.error(f"❌ Exception during fetch_symbols: {e}")
            return None