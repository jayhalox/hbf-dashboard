#!/usr/bin/env python3
"""Fetch 6-month historical data for all 21 HBF stocks, sample to max 60 points each."""
import json
import time
import urllib.request
import math

STOCKS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"),
    ("soul", "357780.KS"), ("tck", "064760.KS"), ("anji", "688019.SS"),
    ("tfme", "002156.SZ"), ("snps", "SNPS"), ("rmbs", "RMBS"), ("ter", "TER"),
    ("adv", "6857.T"), ("tfe", "425420.KS"), ("sol", "473050.KS"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

MAX_POINTS = 60
result = {}

for stock_id, ticker in STOCKS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())

        chart = data.get("chart", {}).get("result", [{}])[0]
        timestamps = chart.get("timestamp", [])
        quotes = chart.get("indicators", {}).get("quote", [{}])[0]
        opens = quotes.get("open", [])
        closes = quotes.get("close", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        volumes = quotes.get("volume", [])

        # Build list of valid data points
        points = []
        for i in range(len(timestamps)):
            c = closes[i] if i < len(closes) else None
            h = highs[i] if i < len(highs) else None
            lv = lows[i] if i < len(lows) else None
            v = volumes[i] if i < len(volumes) else None
            if c is not None:
                points.append({
                    "t": timestamps[i],
                    "c": round(c, 4),
                    "h": round(h, 4) if h is not None else round(c, 4),
                    "l": round(lv, 4) if lv is not None else round(c, 4),
                    "v": v if v is not None else 0,
                })

        # Sample to max 60 points (evenly spaced)
        if len(points) > MAX_POINTS:
            step = (len(points) - 1) / (MAX_POINTS - 1)
            sampled = []
            for j in range(MAX_POINTS):
                idx = min(int(round(j * step)), len(points) - 1)
                sampled.append(points[idx])
            points = sampled

        result[stock_id] = points
        print(f"OK  {stock_id:6s} {ticker:12s} {len(points)} points (from {len(timestamps)} raw)")
    except Exception as e:
        print(f"ERR {stock_id:6s} {ticker:12s} {e}")
        result[stock_id] = []

    time.sleep(0.3)

# Write to data.json
with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(result, f, separators=(",", ":"))

print(f"\nWrote data.json with {len(result)} stocks")
# Print sizes
for sid, pts in result.items():
    print(f"  {sid}: {len(pts)} pts")
