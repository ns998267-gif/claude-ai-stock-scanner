import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

def _scan_one(symbol, interval, min_volume_ratio):
    ticker = f"{symbol}.NS"
    period = "60d" if interval == "5m" else "1y"
    try:
        df = yf.download(ticker, period=period, interval=interval,
                         auto_adjust=True, progress=False, threads=False)
        if df is None or df.empty or len(df) < 30:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        close = df["Close"].astype(float)
        high = df["High"].astype(float)
        volume = df["Volume"].astype(float)
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema20 = close.ewm(span=20, adjust=False).mean()
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        # Compare latest bar with the preceding 20 bars, excluding current bar.
        prior_high = high.shift(1).rolling(20).max().iloc[-1]
        avg_vol = volume.shift(1).rolling(20).mean().iloc[-1]
        last_close = float(close.iloc[-1])
        last_vol = float(volume.iloc[-1])
        vol_ratio = last_vol / avg_vol if avg_vol and not np.isnan(avg_vol) else np.nan
        breakout = last_close > prior_high if not np.isnan(prior_high) else False
        trend = float(ema9.iloc[-1]) > float(ema20.iloc[-1])
        momentum = trend and 50 <= float(rsi.iloc[-1]) <= 80
        if not (breakout or (momentum and vol_ratio >= min_volume_ratio)):
            return None
        return {
            "Symbol": symbol, "Last close": round(last_close, 2),
            "20-bar high breakout": bool(breakout),
            "Relative volume": round(float(vol_ratio), 2) if not np.isnan(vol_ratio) else None,
            "RSI(14)": round(float(rsi.iloc[-1]), 1) if not np.isnan(rsi.iloc[-1]) else None,
            "EMA 9 > EMA 20": bool(trend),
            "Setup": "Breakout" if breakout else "Momentum + volume"
        }
    except Exception:
        return None

def scan_universe(symbols, interval="1d", min_volume_ratio=1.5):
    rows = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(_scan_one, s, interval, min_volume_ratio) for s in symbols]
        for future in as_completed(futures):
            item = future.result()
            if item:
                rows.append(item)
    if not rows:
        return pd.DataFrame(columns=["Symbol","Last close","20-bar high breakout","Relative volume","RSI(14)","EMA 9 > EMA 20","Setup"])
    return pd.DataFrame(rows).sort_values(["20-bar high breakout","Relative volume"], ascending=False)
