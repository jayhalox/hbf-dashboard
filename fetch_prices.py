import json, urllib.request, time

TICKERS = [
    "000660.KS", "005930.KS", "WDC", "MU", "AMAT", "8035.T", "ASML", "ASM",
    "042700.KS", "031980.KS", "ENTG", "357780.KS", "064760.KS", "688019.SS",
    "002156.SZ", "SNPS", "RMBS", "TER", "6857.T", "425420.KS", "473050.KS"
]

results = {}
for ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        result = data['chart']['result'][0]
        meta = result['meta']
        closes = result['indicators']['quote'][0]['close']
        ts = result['timestamp']
        valid = [(ts[i], closes[i]) for i in range(len(closes)) if closes[i] is not None]
        if len(valid) >= 2:
            latest = valid[-1][1]
            prev = valid[-2][1]
        elif len(valid) == 1:
            latest = prev = valid[0][1]
        else:
            latest = meta.get('regularMarketPrice', 0)
            prev = meta.get('previousClose', 0)
        chg = latest - prev
        chgPct = (chg / prev * 100) if prev else 0
        results[ticker] = {"price": latest, "prev": prev, "chg": chg, "chgPct": chgPct}
        print(f"{ticker}|{latest}|{prev}|{chg}|{chgPct:.4f}")
    except Exception as e:
        results[ticker] = {"error": str(e)}
        print(f"{ticker}|ERROR:{e}")
    time.sleep(0.3)

# Save to file for next step
with open("/opt/data/hermes/hbf_dashboard/fetch_results.json", "w") as f:
    json.dump(results, f)

print("\n--- DONE ---")
print(f"Success: {sum(1 for v in results.values() if 'price' in v)} / {len(TICKERS)}")
print(f"Errors: {sum(1 for v in results.values() if 'error' in v)}")
