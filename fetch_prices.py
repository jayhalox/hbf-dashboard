#!/usr/bin/env python3
"""Fetch current prices for all 21 HBF stocks via Yahoo Finance API."""
import json, urllib.request, sys, time

STOCKS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"),
    ("soul", "357780.KS"), ("tck", "064760.KS"), ("anji", "688019.SS"),
    ("tfme", "002156.SZ"), ("snps", "SNPS"), ("rmbs", "RMBS"), ("ter", "TER"),
    ("adv", "6857.T"), ("tfe", "425420.KS"), ("sol", "473050.KS"),
]

results = []
for sid, ticker in STOCKS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        d = data["chart"]["result"][0]
        meta = d["meta"]
        q = d["indicators"]["quote"][0]
        close = q["close"][-1]
        prev = meta["chartPreviousClose"]
        chg = close - prev
        chg_pct = (chg / prev) * 100 if prev else 0
        results.append({
            "id": sid, "price": round(close, 2), "prev": round(prev, 2),
            "chg": round(chg, 2), "chgPct": round(chg_pct, 2)
        })
        print(f"OK  {sid:6s} price={close:>10.2f}  prev={prev:>10.2f}  chg={chg:>+8.2f}  chgPct={chg_pct:>+7.2f}%", flush=True)
    except Exception as e:
        print(f"FAIL {sid:6s}  {e}", flush=True)
        results.append({"id": sid, "error": str(e)})
    time.sleep(0.3)  # be polite to API

with open("/opt/data/hermes/hbf_dashboard/price_data.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved {len(results)} results to price_data.json", flush=True)
