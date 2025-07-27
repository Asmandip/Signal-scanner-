import asyncio, aiohttp, json, os, datetime, psutil
from flask import Flask, render_template
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
import pandas as pd
from pymongo import MongoClient
import telegram

load_dotenv()
app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MONGO_URI = os.getenv("MONGO_URI")
CONF_THRESHOLD = float(os.getenv("CONF_THRESHOLD", 0.75))

bot = telegram.Bot(token=TELEGRAM_TOKEN)
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["bitget"]
collection = db["trades"]

status_data = {
    "timestamp": "",
    "cpu": 0,
    "ram": 0,
    "disk": 0,
    "bot_status": "Stopped",
    "trades": 0,
    "total_pnl": 0,
    "last_signal": "None",
    "scanning": []
}

async def fetch_klines(session, symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity=180&productType=umcbl"
    async with session.get(url) as resp:
        data = await resp.json()
        if "data" not in data:
            return None
        df = pd.DataFrame(data["data"], columns=["time", "open", "high", "low", "close", "volume"])
        df = df.iloc[::-1].reset_index(drop=True)
        df["close"] = pd.to_numeric(df["close"])
        df["volume"] = pd.to_numeric(df["volume"])
        return df

def calculate_indicators(df):
    df["rsi"] = RSIIndicator(df["close"]).rsi()
    df["ema"] = EMAIndicator(df["close"]).ema_indicator()
    macd = MACD(df["close"])
    df["macd"] = macd.macd_diff()
    atr = AverageTrueRange(df["high"], df["low"], df["close"])
    df["atr"] = atr.average_true_range()
    return df

def check_signal(df):
    latest = df.iloc[-1]
    conditions = [
        latest["rsi"] < 30,
        latest["close"] > latest["ema"],
        latest["macd"] > 0,
        latest["volume"] > df["volume"].mean()
    ]
    score = sum(conditions) / len(conditions)
    return score, conditions

async def scan_symbol(session, symbol):
    df = await fetch_klines(session, symbol)
    if df is None or df.empty: return None
    df = calculate_indicators(df)
    score, checks = check_signal(df)
    if score >= 0.75:
        return {
            "symbol": symbol,
            "rsi": round(df["rsi"].iloc[-1], 2),
            "score": score,
            "signal": "BUY",
            "time": datetime.datetime.now().isoformat()
        }
    return None

async def scan_all():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            result = await resp.json()
            symbols = [item["symbol"] for item in result["data"][:100]]
            status_data["scanning"] = symbols
        results = await asyncio.gather(*[scan_symbol(session, sym) for sym in symbols])
        return [r for r in results if r]

async def bot_runner():
    while True:
        try:
            results = await scan_all()
            if results:
                for signal in results:
                    msg = f"📢 *Signal:* `{signal['signal']}`\n🔹 *Pair:* `{signal['symbol']}`\n📈 *RSI:* {signal['rsi']}\n✅ Score: {round(signal['score'], 2)}"
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
                    collection.insert_one(signal)
                    status_data["trades"] += 1
                    status_data["last_signal"] = signal["symbol"]
            update_status()
        except Exception as e:
            print(f"[!] ERROR: {e}")
        await asyncio.sleep(60)

def update_status():
    status_data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_data["cpu"] = psutil.cpu_percent()
    status_data["ram"] = psutil.virtual_memory().percent
    status_data["disk"] = psutil.disk_usage('/').percent
    status_data["bot_status"] = "Running"
    with open("status.json", "w") as f:
        json.dump(status_data, f)

@app.route("/status")
def show_status():
    try:
        with open("status.json", "r") as f:
            data = json.load(f)
        return render_template("status.html", data=data)
    except Exception as e:
        return f"<h1>Error loading status: {str(e)}</h1>", 500

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot_runner())
    app.run(host="0.0.0.0", port=8000)