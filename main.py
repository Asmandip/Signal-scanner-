limport asyncio, aiohttp, json, os, datetime, psutil
from flask import Flask, render_template
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
import pandas as pd

load_dotenv()
app = Flask(__name__)

@app.route("/")
def index():
    return "✅ AsmanDip Trading Bot System is Running!"

@app.route("/status")
def show_status():
    try:
        with open("status.json", "r") as f:
            data = json.load(f)
        return render_template("status.html", data=data)
    except Exception as e:
        return f"<h1>Error loading status: {str(e)}</h1>", 500

async def get_market_data(session, symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity=180&productType=umcbl"
    async with session.get(url) as resp:
        if resp.status == 200:
            candles = await resp.json()
            return candles['data']
        return None

def analyze_signals(df):
    df = df[::-1]
    df['close'] = pd.to_numeric(df['close'])
    rsi = RSIIndicator(close=df['close'], window=14).rsi()
    ema = EMAIndicator(close=df['close'], window=20).ema_indicator()
    macd = MACD(close=df['close']).macd()
    atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close']).average_true_range()
    signal = {
        "RSI": float(rsi.iloc[-1]),
        "EMA": float(ema.iloc[-1]),
        "MACD": float(macd.iloc[-1]),
        "ATR": float(atr.iloc[-1]),
    }
    return signal

async def scan_all():
    symbols = ["BTCUSDT", "ETHUSDT", "XRPUSDT", "TRXUSDT", "LINKUSDT"]
    results = []
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            data = await get_market_data(session, symbol)
            if data:
                df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume"])
                indicators = analyze_signals(df)
                results.append({"symbol": symbol, "indicators": indicators})
    return results

async def update_status():
    while True:
        print("🔄 Scanning market...")
        results = await scan_all()

        system_status = {
            "timestamp": str(datetime.datetime.now()),
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "bot_status": "Active",
            "trades_executed": 0,
            "total_pnl": 0,
            "last_signal": results[0] if results else "No signal",
            "scan_results": results
        }

        with open("status.json", "w") as f:
            json.dump(system_status, f, indent=4)
        await asyncio.sleep(10)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(update_status())
    app.run(host="0.0.0.0", port=8000)