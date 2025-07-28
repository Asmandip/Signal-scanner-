
import aiohttp

async def get_bitget_pairs():
    url = https://api.bitget.com/api/v2/mix/market/contracts?productType=usdt-futures
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    symbols = [item["symbol"] for item in data["data"] if "USDT" in item["symbol"]]
                    print(f"🔗 Pairs fetched from Bitget: {len(symbols)}")
                    return symbols
                else:
                    print(f"❌ Failed to fetch pairs | Status: {response.status}")
        except Exception as e:
            print(f"❌ Exception fetching pairs: {e}")
    return []
