
import aiohttp
import os

async def send_telegram_message(message, chat_id):
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status != 200:
                print(f"❌ Failed to send Telegram message: {response.status}")
            else:
                print("✅ Telegram message sent!")
