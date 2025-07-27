# main.py

import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
from aiohttp import ClientSession
from flask import Flask
from bitget_scanner import get_bitget_pairs
from signal_generator import analyze_signals
from telegram_notifier import send_telegram_message
import threading

load_dotenv()

app = Flask(__name__)
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

# ✅ Candle Fetcher
async def fetch_candles(session, symbol):
    try:
        url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity=3m&limit=100"
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
            else:
                print(f"⚠️ Failed to fetch candles for {symbol} | Status: {response.status}")
    except Exception as e:
        print(f"❌ Exception fetching candles for {symbol}: {e}")
    return None

# ✅ Signal Scanner + Telegram Notifier
async def scan_and_signal():
    print("📡 Starting market scan...")
    pairs = await get_bitget_pairs()

    if not pairs:
        print("❌ No futures pairs found!")
        return

    print(f"✅ Total Pairs Fetched: {len(pairs)}")

    async with ClientSession() as session:
        for symbol in pairs:
            print(f"🔍 Scanning {symbol}...")
            df = await fetch_candles(session, symbol)
            if df is None or df.empty:
                print(f"⛔ No valid data for {symbol}")
                continue

            signal_data = analyze_signals(df)
            if signal_data:
                message = (
                    f"📊 <b>Signal Alert for {symbol}</b>\n"
                    f"🔁 Signal: <b>{signal_data['signal']}</b>\n"
                    f"💰 Price: {signal_data['price']}\n"
                    f"📈 RSI: {signal_data['rsi']}\n"
                    f"🛡️ ATR: {signal_data['atr']}\n"
                    f"✅ Confirmations:\n - " + "\n - ".join(signal_data['confirmations'])
                )
                print(f"📤 Sending Telegram Message:\n{message}")
                await send_telegram_message(message, TELEGRAM_CHAT_ID)
            else:
                print(f"🚫 No signal for {symbol}")
            await asyncio.sleep(0.3)

# ✅ Flask Web Route
@app.route('/')
def index():
    return '🚀 Signal Bot is Running!'

# ✅ Flask & Async Loop with Threading
def run_flask():
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

def start_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(scan_and_signal())
    loop.run_forever()

# ✅ Entry Point
if __name__ == '__main__':
    print("🟢 Starting AsmanDip Future Scanner Bot...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    start_loop()