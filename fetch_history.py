#!/usr/bin/env python3
"""Fetch 6-month history for all 21 HBF stocks → data.json (max 60 pts each)"""
import json, urllib.request, time, math, sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

output = {}
MAX_PTS = 60

for stock_id, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        timestamps = result["timestamp"]
        quotes = result["indicators"]["quote"][0]
        opens = quotes.get("open", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        closes = quotes.get("close", [])
        volumes = quotes.get("volume", [])

        # Build list of valid points
        points = []
        for i in range(len(timestamps)):
            t = timestamps[i]
            c = closes[i] if i < len(closes) else None
            h = highs[i] if i < len(highs) else None
            l = lows[i] if i < len(lows) else None
            v = volumes[i] if i < len(volumes) else None
            if c is not None:
                points.append({"t": t, "c": c, "h": h, "l": l, "v": v if v else 0})

        # Sample to max 60 points
        n = len(points)
        if n <= MAX_PTS:
            sampled = points
        else:
            step = (n - 1) / (MAX_PTS - 1)
            sampled = [points[round(i * step)] for i in range(MAX_PTS)]

        output[stock_id] = sampled
        print(f"OK hist: {stock_id} ({ticker}) = {n} raw → {len(sampled)} pts", file=sys.stderr)
    except Exception as e:
        print(f"FAIL hist: {stock_id} ({ticker}): {e}", file=sys.stderr)
        output[stock_id] = []
    time.sleep(0.3)

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(output, f, separators=(",", ":"))
print("data.json written", file=sys.stderr)
