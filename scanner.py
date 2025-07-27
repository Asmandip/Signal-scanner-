import aiohttp
import asyncio
import pandas as pd
import datetime
import time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
from dotenv import load_dotenv
import os
import logging
from utils.telegram import send_telegram_message  # make sure this exists

load_dotenv()

INTERVAL = "3m"
LIMIT = 100
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

HEADERS = {
    "Content-Type": "application/json"
}

async def fetch_klines(session, symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity={INTERVAL}&limit={LIMIT}"
    try:
        async with session.get(url, headers=HEADERS) as resp:
            if resp.status == 200:
                data = await resp.json()
                df = pd.DataFrame(data['data'], columns=[
                    "timestamp", "open", "high", "low", "close", "volume", "quoteVolume"
                ])
                df["close"] = pd.to_numeric(df["close"])
                df["high"] = pd.to_numeric(df["high"])
                df["low"] = pd.to_numeric(df["low"])
                df["open"] = pd.to_numeric(df["open"])
                df["volume"] = pd.to_numeric(df["volume"])
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
    except Exception as e:
        logging.warning(f"Error fetching {symbol}: {str(e)}")
    return None

def analyze_data(df):
    rsi = RSIIndicator(close=df["close"], window=RSI_PERIOD).rsi()
    df["rsi"] = rsi
    macd = MACD(close=df["close"])
    df["macd"] = macd.macd_diff()
    ema = EMAIndicator(close=df["close"], window=20)
    df["ema"] = ema.ema_indicator()
    atr = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=14)
    df["atr"] = atr.average_true_range()
    return df

async def scan_symbol(session, symbol):
    df = await fetch_klines(session, symbol)
    if df is None or len(df) < RSI_PERIOD:
        return

    df = analyze_data(df)
    last = df.iloc[-1]

    confirmations = 0
    reasons = []

    if last["rsi"] <= RSI_OVERSOLD:
        confirmations += 1
        reasons.append(f"🔻 RSI: {round(last['rsi'],2)}")

    if last["rsi"] >= RSI_OVERBOUGHT:
        confirmations += 1
        reasons.append(f"🔺 RSI: {round(last['rsi'],2)}")

    if last["close"] > last["ema"]:
        confirmations += 1
        reasons.append("📈 Above EMA")

    if last["macd"] > 0:
        confirmations += 1
        reasons.append("✅ MACD Bullish")

    if confirmations >= 3:
        direction = "BUY" if last["rsi"] < 50 else "SELL"
        signal = f"""
📡 Signal Alert: {symbol}
📊 Action: {direction}
🧠 Confirmations: {confirmations}/4
{chr(10).join(reasons)}
📈 Price: {round(last['close'], 4)}
🕒 Time: {last['timestamp'].strftime('%H:%M:%S')}
"""
        await send_telegram_message(signal)

async def run_scanner():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            all_symbols = [x["symbol"] for x in data["data"]]

        top_100 = all_symbols[:100]
        logging.info("🚀 Scanning Top 100 Symbols...")

        tasks = [scan_symbol(session, symbol) for symbol in top_100]
        await asyncio.gather(*tasks)