import threading
import asyncio
from flask import Flask
from signal_generator import analyze_signals
from bitget_scanner import get_bitget_pairs
from telegram_notifier import send_telegram_message
import pandas as pd
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

@app.route('/')
def index():
    return '✅ AsmanDip Signal Bot is Running.'

@app.route('/status')
def status():
    return '📡 Bot Status: Active & Scanning!'

async def fetch_candles(session, symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity=3m&limit=100"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                df = pd.DataFrame(data['data'])
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                df = df.iloc[::-1]
                df["close"] = pd.to_numeric(df["close"])
                df["high"] = pd.to_numeric(df["high"])
                df["low"] = pd.to_numeric(df["low"])
                return df
    except Exception as e:
        print(f"❌ Error fetching candles for {symbol}: {e}")
    return None

async def scanner_loop():
    print("📡 Scanner started...")
    while True:
        try:
            pairs = await get_bitget_pairs()
            if not pairs:
                print("⚠️ No pairs found.")
                await asyncio.sleep(60)
                continue

            async with aiohttp.ClientSession() as session:
                for symbol in pairs:
                    df = await fetch_candles(session, symbol)
                    if df is None or df.empty:
                        continue

                    signal = analyze_signals(df)
                    if signal:
                        msg = (
                            f"📊 Signal Alert for {symbol}\n"
                            f"🔁 Signal: {signal['signal']}\n"
                            f"💰 Price: {signal['price']}\n"
                            f"📈 RSI: {signal['rsi']}\n"
                            f"🛡️ ATR: {signal['atr']}\n"
                            f"✅ Confirmations:\n - " + "\n - ".join(signal['confirmations'])
                        )
                        print(msg)
                        await send_telegram_message(msg, TELEGRAM_CHAT_ID)
                    await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ Scanner error: {e}")
        await asyncio.sleep(60)  # Repeat every 60 seconds

def run_async_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scanner_loop())

if __name__ == "__main__":
    print("🟢 Starting AsmanDip Future Scanner Bot...")

    # Async scanner runs in background
    threading.Thread(target=run_async_loop).start()

    # Flask server runs here
    app.run(host='0.0.0.0', port=8000)