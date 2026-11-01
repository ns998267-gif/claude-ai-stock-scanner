from pathlib import Path
import os

def load_symbols():
    path = Path("data/watchlist.txt")
    if not path.exists():
        return ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
                "SBIN", "LT", "AXISBANK", "BHARTIARTL", "ITC",
                "TATAMOTORS", "MARUTI", "SUNPHARMA", "BAJFINANCE", "TITAN"]
    return [x.strip().upper() for x in path.read_text().splitlines()
            if x.strip() and not x.strip().startswith("#")]
