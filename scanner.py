import aiohttp
import asyncio
import logging
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, MACD
from ta.volatility import AverageTrueRange
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)

async def fetch_tickers():
    url = "https://api.bitget.com/api/v2/mix/market/tickers?productType=umcbl"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                logging.error(f"❌ Ticker fetch failed: {resp.status} - {text}")
                return []
            data = await resp.json()
            return data.get("data", [])

async def fetch_kline(symbol):
    url = f"https://api.bitget.com/api/v2/mix/market/candles?symbol={symbol}&granularity=3m"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                logging.warning(f"❌ Failed to fetch kline for {symbol}")
                return None
            result = await resp.json()
            return result.get("data", [])

def analyze_data(kline_data):
    if len(kline_data) < 50:
        return None

    df = pd.DataFrame(kline_data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "quoteVol"
    ])
    df = df.astype(float)
    df["rsi"] = RSIIndicator(df["close"], window=14).rsi()
    df["ema_20"] = EMAIndicator(df["close"], window=20).ema_indicator()
    df["macd"] = MACD(df["close"]).macd()
    df["macd_signal"] = MACD(df["close"]).macd_signal()
    df["atr"] = AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range()

    # Confirmation logic
    latest = df.iloc[-1]
    confirmations = 0

    # RSI oversold/buy condition
    if latest["rsi"] < 30:
        confirmations += 1

    # Price crosses above EMA
    if latest["close"] > latest["ema_20"]:
        confirmations += 1

    # MACD bullish crossover
    if latest["macd"] > latest["macd_signal"]:
        confirmations += 1

    # Volume spike
    vol_avg = df["volume"].rolling(window=10).mean().iloc[-1]
    if latest["volume"] > 1.5 * vol_avg:
        confirmations += 1

    # Optional: candlestick pattern check (simple example)
    if (latest["close"] > latest["open"]) and ((latest["close"] - latest["open"]) > 0.5 * (latest["high"] - latest["low"])):
        confirmations += 1

    return {
        "confirmations": confirmations,
        "rsi": round(latest["rsi"], 2),
        "ema": round(latest["ema_20"], 2),
        "macd": round(latest["macd"], 2),
        "macd_signal": round(latest["macd_signal"], 2),
        "volume": round(latest["volume"], 2),
        "atr": round(latest["atr"], 2),
        "close": round(latest["close"], 4),
    }

async def scan_market():
    results = []
    tickers = await fetch_tickers()
    if not tickers:
        return results

    top_symbols = [x["symbol"] for x in tickers if "USDT" in x["symbol"]][:100]

    for symbol in top_symbols:
        kline_data = await fetch_kline(symbol)
        if kline_data:
            signal = analyze_data(kline_data)
            if signal and signal["confirmations"] >= 4:
                results.append((symbol, signal))
    return results