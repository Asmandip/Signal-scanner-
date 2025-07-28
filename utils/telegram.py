import os
import aiohttp
import asyncio

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# utils/telegram.py

def send_telegram_message(msg):
    print(f"Sending message: {msg}")

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    print(f"Telegram Error: {await resp.text()}")
        except Exception as e:
            print(f"Telegram Send Failed: {e}")