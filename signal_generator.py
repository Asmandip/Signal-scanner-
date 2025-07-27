import pandas as pd
from ta.momentum import RSIIndicator

def analyze_signals(df):
    try:
        close = df['close']
        high = df['high']
        low = df['low']

        rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
        atr = (high - low).rolling(window=14).mean().iloc[-1]

        confirmations = []
        if rsi < 30:
            confirmations.append("RSI Oversold")
        elif rsi > 70:
            confirmations.append("RSI Overbought")

        if confirmations:
            return {
                "signal": "BUY" if rsi < 30 else "SELL",
                "price": close.iloc[-1],
                "rsi": round(rsi, 2),
                "atr": round(atr, 2),
                "confirmations": confirmations
            }
    except Exception as e:
        print(f"⚠️ Error in signal generation: {e}")
    return None