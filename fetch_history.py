#!/usr/bin/env python3
"""Fetch 6-month historical data for all 21 HBF stocks. Sample to max 60 points each."""
import json
import urllib.request
import time

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS",
}

result = {}

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        chart = data["chart"]["result"][0]
        timestamps = chart["timestamp"]
        quotes = chart["indicators"]["quote"][0]
        opens = quotes["open"]
        highs = quotes["high"]
        lows = quotes["low"]
        closes = quotes["close"]
        volumes = quotes["volume"]

        points = []
        for i in range(len(timestamps)):
            c = closes[i] if closes[i] is not None else (opens[i] if opens[i] is not None else None)
            if c is None:
                continue
            points.append({
                "t": timestamps[i],
                "c": round(c, 2),
                "h": round(highs[i], 2) if highs[i] is not None else round(c, 2),
                "l": round(lows[i], 2) if lows[i] is not None else round(c, 2),
                "v": volumes[i] if volumes[i] is not None else 0,
            })

        # Sample to max 60 points (evenly spaced)
        n = len(points)
        if n > 60:
            step = (n - 1) / 59
            sampled = []
            indices = set()
            for j in range(60):
                idx = min(round(j * step), n - 1)
                if idx not in indices:
                    indices.add(idx)
                    sampled.append(points[idx])
            # Always include first and last
            if 0 not in indices:
                sampled[0] = points[0]
            if (n - 1) not in indices:
                sampled[-1] = points[-1]
            points = sampled

        result[sid] = points
        print(f"HIST OK  {sid:6s} {ticker:12s} {n} raw -> {len(points)} sampled")
    except Exception as e:
        print(f"HIST ERR {sid:6s} {ticker:12s} {e}")

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(result, f)
print(f"\nWritten {sum(len(v) for v in result.values())} total points to data.json")
