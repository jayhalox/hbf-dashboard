#!/usr/bin/env python3
"""Fetch all 21 HBF stocks from Yahoo Finance and output JSON."""
import json, urllib.request, time, sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

results = {}

for stock_id, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        quotes = result["indicators"]["quote"][0]
        close = quotes["close"][-1]
        if close is None:
            # Try second-to-last
            close = quotes["close"][-2]
        prev = meta.get("previousClose") or meta.get("chartPreviousClose") or close
        chg = round(close - prev, 2) if close and prev else 0
        chgPct = round((chg / prev) * 100, 2) if prev and prev != 0 else 0
        results[stock_id] = {
            "ticker": ticker, "price": close, "prev": prev,
            "chg": chg, "chgPct": chgPct
        }
        print(f"OK: {stock_id} ({ticker}) = {close}", file=sys.stderr)
    except Exception as e:
        print(f"FAIL: {stock_id} ({ticker}): {e}", file=sys.stderr)
        results[stock_id] = {"ticker": ticker, "price": None, "prev": None, "chg": 0, "chgPct": 0}
    time.sleep(0.3)  # Be polite to the API

print(json.dumps(results, indent=2))
