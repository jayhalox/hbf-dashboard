import json, urllib.request, sys

TICKERS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"),
    ("soul", "357780.KS"), ("tck", "064760.KS"), ("anji", "688019.SS"),
    ("tfme", "002156.SZ"), ("snps", "SNPS"), ("rmbs", "RMBS"), ("ter", "TER"),
    ("adv", "6857.T"), ("tfe", "425420.KS"), ("sol", "473050.KS"),
]

results = {}
for sid, ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        d = data["chart"]["result"][0]
        meta = d["meta"]
        quotes = d["indicators"]["quote"][0]
        ts = d["timestamp"]
        price = meta["regularMarketPrice"]
        # Use chartPreviousClose (new key name) or fallback
        prev = meta.get("chartPreviousClose") or meta.get("regularMarketPreviousClose") or meta.get("previousClose")
        if prev is None:
            raise KeyError("previousClose not found in meta")
        chg = price - prev
        chg_pct = (chg / prev) * 100
        results[sid] = {
            "ticker": ticker, "price": price, "prev": prev,
            "chg": round(chg, 2), "chgPct": round(chg_pct, 2),
            "ts": ts, "open": quotes["open"], "high": quotes["high"],
            "low": quotes["low"], "close": quotes["close"], "volume": quotes["volume"]
        }
        print(f"OK: {sid} ({ticker}) price={price}, prev={prev}, chg={round(chg,2)}, chgPct={round(chg_pct,2)}%")
    except Exception as e:
        print(f"FAIL: {sid} ({ticker}): {e}", file=sys.stderr)
        results[sid] = {"error": str(e)}

with open("/opt/data/hermes/hbf_dashboard/price_data.json", "w") as f:
    json.dump(results, f, indent=2)

summary = {}
for sid, r in results.items():
    if "error" not in r:
        summary[sid] = {"price": r["price"], "prev": r["prev"], "chg": r["chg"], "chgPct": r["chgPct"]}

with open("/opt/data/hermes/hbf_dashboard/price_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n--- SUMMARY ---")
print(json.dumps(summary, indent=2))
print(f"Done. Fetched {len(summary)} of {len(TICKERS)} stocks.")
