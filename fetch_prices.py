#!/usr/bin/env python3
"""Fetch current prices for all 21 HBF stocks from Yahoo Finance."""
import json
import urllib.request
import sys

TICKERS = [
    ("sk", "000660.KS"),
    ("ss", "005930.KS"),
    ("wdc", "WDC"),
    ("mu", "MU"),
    ("amat", "AMAT"),
    ("tel", "8035.T"),
    ("asml", "ASML"),
    ("asmi", "ASM"),
    ("hanmi", "042700.KS"),
    ("psk", "031980.KS"),
    ("entg", "ENTG"),
    ("soul", "357780.KS"),
    ("tck", "064760.KS"),
    ("anji", "688019.SS"),
    ("tfme", "002156.SZ"),
    ("snps", "SNPS"),
    ("rmbs", "RMBS"),
    ("ter", "TER"),
    ("adv", "6857.T"),
    ("tfe", "425420.KS"),
    ("sol", "473050.KS"),
]

results = {}

for sid, ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "Mozilla/5.0")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        chart = data["chart"]["result"][0]
        meta = chart["meta"]
        quotes = chart["indicators"]["quote"][0]
        i = -1
        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]
        chg = price - prev
        chg_pct = round((chg / prev) * 100, 2)
        results[sid] = {
            "ticker": ticker,
            "price": price,
            "prev": prev,
            "chg": chg,
            "chgPct": chg_pct,
        }
        print(f"OK  {sid:6s} {ticker:12s} price={price}")
    except Exception as e:
        print(f"ERR {sid:6s} {ticker:12s} {e}", file=sys.stderr)
        results[sid] = {"ticker": ticker, "error": str(e)}

print("\n---JSON---")
print(json.dumps(results, indent=2))
