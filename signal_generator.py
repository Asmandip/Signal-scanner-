
def analyze_signals(df):
    try:
        close_prices = df['close']
        rsi = close_prices.pct_change().rolling(window=14).mean().iloc[-1] * 100
        atr = (df['high'] - df['low']).rolling(window=14).mean().iloc[-1]

        confirmations = []
        if rsi < 30:
            confirmations.append("RSI Oversold")
        elif rsi > 70:
            confirmations.append("RSI Overbought")

        if len(confirmations) >= 1:
            return {
                "signal": "BUY" if rsi < 30 else "SELL",
                "price": close_prices.iloc[-1],
                "rsi": round(rsi, 2),
                "atr": round(atr, 2),
                "confirmations": confirmations
            }
    except Exception as e:
        print(f"⚠️ Error in signal analysis: {e}")
    return None
