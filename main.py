import asyncio
from scanner import scan_market
from telegram_bot import send_telegram_alert
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ AsmanDip Bot is Running..."

async def main_loop():
    while True:
        try:
            print("🔍 Scanning market...")
            signals = await scan_market()
            for symbol, signal in signals:
                msg = (
                    f"📈 *Signal: {symbol}*\n"
                    f"🟢 Confirmations: {signal['confirmations']}/5\n"
                    f"💵 Close: {signal['close']}\n"
                    f"📉 RSI: {signal['rsi']}\n"
                    f"📊 EMA(20): {signal['ema']}\n"
                    f"📈 MACD: {signal['macd']}, Signal: {signal['macd_signal']}\n"
                    f"📦 Volume: {signal['volume']}\n"
                    f"🌊 ATR: {signal['atr']}\n"
                    f"#bitget #future #signal"
                )
                await send_telegram_alert(msg)
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
        await asyncio.sleep(180)  # every 3 minutes

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main_loop())
    app.run(host="0.0.0.0", port=8000)