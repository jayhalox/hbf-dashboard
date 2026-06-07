#!/usr/bin/env python3
"""Fetch current prices for all 21 HBF stocks from Yahoo Finance."""
import json
import time
import urllib.request
import urllib.error

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

results = {}

for stock_id, ticker in STOCKS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        chart = data.get("chart", {}).get("result", [{}])[0]
        meta = chart.get("meta", {})
        quotes = chart.get("indicators", {}).get("quote", [{}])[0]
        
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("previousClose")
        
        if price is not None and prev_close is not None and prev_close != 0:
            chg = round(price - prev_close, 2)
            chg_pct = round((chg / prev_close) * 100, 2)
        else:
            # Try from quotes
            closes = [c for c in quotes.get("close", []) if c is not None]
            if len(closes) >= 2:
                price = closes[-1]
                prev_close = closes[-2]
                chg = round(price - prev_close, 2)
                chg_pct = round((chg / prev_close) * 100, 2) if prev_close != 0 else 0
            else:
                chg, chg_pct = 0, 0
        
        results[stock_id] = {
            "ticker": ticker,
            "price": price,
            "prev": prev_close,
            "chg": chg,
            "chgPct": chg_pct,
        }
        print(f"OK  {stock_id:6s} {ticker:12s} price={price} prev={prev_close} chg={chg} ({chg_pct}%)")
    except Exception as e:
        print(f"ERR {stock_id:6s} {ticker:12s} {e}")
        results[stock_id] = {"ticker": ticker, "error": str(e)}
    
    time.sleep(0.5)  # Rate limit

# Output as JSON for next step
print("\n=== JSON ===")
print(json.dumps(results, indent=2, default=str))
