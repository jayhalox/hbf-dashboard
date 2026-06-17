#!/usr/bin/env python3
"""Fetch current stock prices from Yahoo Finance API."""
import json
import urllib.request
import sys
import time

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

results = {}

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        result = data["chart"]["result"][0]
        meta = result["meta"]
        
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        
        chg = None
        chg_pct = None
        if price is not None and prev_close is not None and prev_close != 0:
            chg = round(price - prev_close, 4)
            chg_pct = round((chg / prev_close) * 100, 2)
        
        results[sid] = {
            "price": price,
            "prev": prev_close,
            "chg": chg,
            "chgPct": chg_pct,
            "currency": meta.get("currency"),
            "exchange": meta.get("exchangeName"),
        }
        print(f"[OK] {sid} ({ticker}): price={price}, prev={prev_close}, chg={chg}, chgPct={chg_pct}%", file=sys.stderr)
    except Exception as e:
        print(f"[ERR] {sid} ({ticker}): {e}", file=sys.stderr)
        results[sid] = {"error": str(e)}
    time.sleep(0.3)

print(json.dumps(results, indent=2))
