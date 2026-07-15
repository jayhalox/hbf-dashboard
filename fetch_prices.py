import json, sys, urllib.request, time

TICKERS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"), ("soul", "357780.KS"),
    ("tck", "064760.KS"), ("anji", "688019.SS"), ("tfme", "002156.SZ"), ("snps", "SNPS"),
    ("rmbs", "RMBS"), ("ter", "TER"), ("adv", "6857.T"), ("tfe", "425420.KS"),
    ("sol", "473050.KS")
]

results = {}

for stock_id, ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read().decode())
        r = d['chart']['result'][0]
        meta = r['meta']
        quotes = r['indicators']['quote'][0]
        closes = quotes['close']
        highs = quotes['high']
        lows = quotes['low']
        volumes = quotes['volume']
        timestamps = r['timestamp']

        prev_close = meta.get('chartPreviousClose', None)

        recent_close = None
        recent_high = None
        recent_low = None
        recent_vol = None
        for i in range(len(closes)-1, -1, -1):
            if closes[i] is not None:
                recent_close = closes[i]
                recent_high = highs[i]
                recent_low = lows[i]
                recent_vol = volumes[i]
                break

        prev = prev_close
        if prev is None:
            valid = [c for c in closes if c is not None]
            if len(valid) >= 2:
                prev = valid[-2]

        chg = round(recent_close - prev, 2) if recent_close and prev else 0
        chg_pct = round((chg / prev) * 100, 2) if prev and prev != 0 else 0

        results[stock_id] = {
            "price": recent_close,
            "prev": prev,
            "chg": chg,
            "chgPct": chg_pct,
            "high": recent_high,
            "low": recent_low,
            "volume": recent_vol,
            "timestamp": timestamps[-1]
        }
        print(f"OK: {stock_id} ({ticker}) = {recent_close}, chg={chg} ({chg_pct}%)")
    except Exception as e:
        print(f"ERR: {stock_id} ({ticker}): {e}")
        results[stock_id] = {"error": str(e)}

    time.sleep(0.3)

print("\n--- JSON ---")
print(json.dumps(results, indent=2))
