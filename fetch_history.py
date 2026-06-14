#!/usr/bin/env python3
"""Fetch 6-month historical data for 21 HBF stocks, generate data.json (max 60 pts/stock)."""
import json, urllib.request, time, math

STOCKS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"),
    ("soul", "357780.KS"), ("tck", "064760.KS"), ("anji", "688019.SS"),
    ("tfme", "002156.SZ"), ("snps", "SNPS"), ("rmbs", "RMBS"), ("ter", "TER"),
    ("adv", "6857.T"), ("tfe", "425420.KS"), ("sol", "473050.KS"),
]

MAX_POINTS = 60
results = {}

for sid, ticker in STOCKS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        d = data["chart"]["result"][0]
        timestamps = d["timestamp"]
        q = d["indicators"]["quote"][0]
        opens = q["open"]
        highs = q["high"]
        lows = q["low"]
        closes = q["close"]
        volumes = q["volume"]

        points = []
        n = len(timestamps)
        step = max(1, n // MAX_POINTS) if n > MAX_POINTS else 1

        for i in range(0, n, step):
            c = closes[i]
            if c is None:
                continue
            points.append({
                "t": timestamps[i],
                "c": round(c, 2),
                "h": round(highs[i], 2) if highs[i] else round(c, 2),
                "l": round(lows[i], 2) if lows[i] else round(c, 2),
                "v": volumes[i] if volumes[i] else 0
            })
            if len(points) >= MAX_POINTS:
                break

        # ensure last point is included
        last_c = closes[-1]
        if last_c is not None and (not points or points[-1]["t"] != timestamps[-1]):
            points.append({
                "t": timestamps[-1],
                "c": round(last_c, 2),
                "h": round(highs[-1], 2) if highs[-1] else round(last_c, 2),
                "l": round(lows[-1], 2) if lows[-1] else round(last_c, 2),
                "v": volumes[-1] if volumes[-1] else 0
            })
            if len(points) > MAX_POINTS:
                points = points[:MAX_POINTS]

        results[sid] = points
        print(f"OK  {sid:6s}  {len(points)} points  ({ticker})", flush=True)
    except Exception as e:
        print(f"FAIL {sid:6s}  {e}", flush=True)
        results[sid] = []
    time.sleep(0.3)

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(results, f)
print(f"\nSaved {sum(1 for v in results.values() if v)}/21 stocks to data.json", flush=True)
