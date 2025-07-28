import os
import aiohttp
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
from datetime import datetime
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def fetch_klines(session, symbol, interval="3m", limit=100):
    try:
        url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity={interval}&limit={limit}"
        async with session.get(url) as res:
            if res.status != 200:
                logging.warning(f"Failed to fetch klines for {symbol}: {res.status}")
                return None
            data = await res.json()
            df = pd.DataFrame(data["data"], columns=["timestamp", "open", "high", "low", "close", "volume", "quoteVolume"])
            df = df.iloc[::-1]  # Reverse
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)
            return df
    except Exception as e:
        logging.error(f"Error fetching klines: {e}")
        return None

def analyze_data(df):
    try:
        df["rsi"] = RSIIndicator(close=df["close"]).rsi()
        df["ema20"] = EMAIndicator(close=df["close"], window=20).ema_indicator()
        df["macd"] = MACD(close=df["close"]).macd()
        df["atr"] = AverageTrueRange(high=df["high"].astype(float), low=df["low"].astype(float), close=df["close"]).average_true_range()

        rsi = df["rsi"].iloc[-1]
        macd = df["macd"].iloc[-1]
        ema = df["ema20"].iloc[-1]
        price = df["close"].iloc[-1]

        confirmations = 0
        if rsi < 30:
            confirmations += 1
        if price > ema:
            confirmations += 1
        if macd > 0:
            confirmations += 1
        if df["volume"].iloc[-1] > df["volume"].mean():
            confirmations += 1

        if confirmations >= 3:
            return "BUY"
        elif rsi > 70 and confirmations >= 3:
            return "SELL"
        return None
    except Exception as e:
        logging.error(f"Error analyzing data: {e}")
        return None

async def send_telegram_signal(symbol, signal):
    try:
        text = f"📢 Signal: {signal}\n🪙 Symbol: {symbol}\n⏱️ Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text
        }
        async with aiohttp.ClientSession() as session:
            await session.post(url, json=payload)
    except Exception as e:
        logging.error(f"Failed to send telegram message: {e}")