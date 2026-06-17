#!/usr/bin/env python3
"""Fetch 6-month historical OHLCV data from Yahoo Finance and generate data.json.
Samples to max 60 points per stock."""
import json
import urllib.request
import time
import sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

MAX_POINTS = 60
result = {}
errors = []

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        
        chart = data["chart"]["result"][0]
        timestamps = chart["timestamp"]
        quotes = chart["indicators"]["quote"][0]
        
        opens = quotes.get("open", [])
        highs = quotes.get("high", [])
        lows = quotes.get("low", [])
        closes = quotes.get("close", [])
        volumes = quotes.get("volume", [])
        
        raw = []
        for i in range(len(timestamps)):
            c = closes[i] if i < len(closes) and closes[i] is not None else None
            if c is None:
                continue
            raw.append({
                "t": timestamps[i],
                "c": c,
                "h": highs[i] if i < len(highs) and highs[i] is not None else c,
                "l": lows[i] if i < len(lows) and lows[i] is not None else c,
                "v": volumes[i] if i < len(volumes) and volumes[i] is not None else 0,
            })
        
        # Sample down to MAX_POINTS keeping first and last
        n = len(raw)
        if n > MAX_POINTS:
            step = (n - 1) / (MAX_POINTS - 1)
            sampled = []
            for j in range(MAX_POINTS):
                idx = min(n - 1, int(round(j * step)))
                sampled.append(raw[idx])
            raw = sampled
        
        result[sid] = raw
        print(f"[HIST] {sid} ({ticker}): {n} raw -> {len(raw)} points", file=sys.stderr)
    except Exception as e:
        err_msg = f"[ERR] {sid} ({ticker}): {e}"
        print(err_msg, file=sys.stderr)
        errors.append(err_msg)
        result[sid] = []
    
    time.sleep(0.4)

# Write
output_path = "/opt/data/hermes/hbf_dashboard/data.json"
with open(output_path, "w") as f:
    json.dump(result, f, separators=(",", ":"))

print(f"\nDone. {len(result)} stocks written to {output_path}", file=sys.stderr)
if errors:
    print(f"Errors: {len(errors)}", file=sys.stderr)
    for e in errors:
        print(f"  {e}", file=sys.stderr)

# Print summary
for sid in sorted(result.keys()):
    pts = len(result[sid])
    label = f"{sid} ({TICKERS[sid]})"
    if pts > 0:
        first = result[sid][0]
        last = result[sid][-1]
        pct = round((last["c"] - first["c"]) / first["c"] * 100, 2) if first["c"] else 0
        print(f"  {label}: {pts} pts | {first['c']} -> {last['c']} ({pct:+.2f}%)", file=sys.stderr)
    else:
        print(f"  {label}: NO DATA", file=sys.stderr)
