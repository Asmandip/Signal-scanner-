# signal_generator.py

import pandas as pd

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_signals(df):
    try:
        df['rsi'] = compute_rsi(df['close'])
        rsi = df['rsi'].iloc[-1]
        atr = (df['high'] - df['low']).rolling(window=14).mean().iloc[-1]

        confirmations = []
        if rsi < 30:
            confirmations.append("RSI Oversold")
        elif rsi > 70:
            confirmations.append("RSI Overbought")

        if confirmations:
            print(f"✅ Signal generated | RSI: {round(rsi, 2)} | ATR: {round(atr, 2)}")
            return {
                "signal": "BUY" if rsi < 30 else "SELL",
                "price": df['close'].iloc[-1],
                "rsi": round(rsi, 2),
                "atr": round(atr, 2),
                "confirmations": confirmations
            }
    except Exception as e:
        print(f"⚠️ Error in signal analysis: {e}")
    return None