#!/usr/bin/env python3
"""Fetch current prices for all 21 HBF stocks via Yahoo Finance API."""
import json
import urllib.request
import urllib.error
import time
import sys

STOCKS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

def fetch_one(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        meta = result['meta']
        quotes = result['indicators']['quote'][0]
        timestamps = result['timestamp']
        
        # Get the last two close prices for chg calculation
        closes = quotes['close']
        # Remove None values
        valid_closes = [c for c in closes if c is not None]
        
        if len(valid_closes) >= 2:
            price = valid_closes[-1]
            prev = valid_closes[-2]
            chg = price - prev
            chg_pct = (chg / prev) * 100
        elif len(valid_closes) == 1:
            price = valid_closes[0]
            prev = price
            chg = 0
            chg_pct = 0
        else:
            return None
        
        return {
            'price': price,
            'prev': prev,
            'chg': chg,
            'chgPct': chg_pct,
            'currency': meta.get('currency', ''),
            'marketPrice': meta.get('regularMarketPrice', price),
            'prevClose': meta.get('chartPreviousClose', prev)
        }
    except Exception as e:
        print(f"ERROR fetching {ticker}: {e}", file=sys.stderr)
        return None

# Fetch all stocks
results = {}
for stock_id, ticker in STOCKS.items():
    print(f"Fetching {stock_id} ({ticker})...", file=sys.stderr)
    result = fetch_one(ticker)
    if result:
        results[stock_id] = result
        print(f"  -> price={result['price']}, prev={result['prev']}, chg={result['chg']:.2f}, chgPct={result['chgPct']:.2f}%", file=sys.stderr)
    else:
        print(f"  -> FAILED", file=sys.stderr)
    time.sleep(0.5)  # Rate limiting

# Save results
with open('/opt/data/hermes/hbf_dashboard/current_prices.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nDone! Fetched {len(results)}/{len(STOCKS)} stocks.", file=sys.stderr)
print(json.dumps(results, indent=2))
