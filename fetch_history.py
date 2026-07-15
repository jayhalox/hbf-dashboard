import json, urllib.request, time, math

STOCKS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM.AS"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"), ("soul", "357780.KS"),
    ("tck", "064760.KS"), ("anji", "688019.SS"), ("tfme", "002156.SZ"), ("snps", "SNPS"),
    ("rmbs", "RMBS"), ("ter", "TER"), ("adv", "6857.T"), ("tfe", "425420.KS"),
    ("sol", "473050.KS")
]

MAX_POINTS = 60
output = {}

for stock_id, ticker in STOCKS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode())
        r = d['chart']['result'][0]
        timestamps = r['timestamp']
        quotes = r['indicators']['quote'][0]
        closes = quotes['close']
        highs = quotes['high']
        lows = quotes['low']
        volumes = quotes['volume']

        points = []
        for i in range(len(timestamps)):
            if closes[i] is not None:
                points.append({
                    "t": timestamps[i],
                    "c": closes[i],
                    "h": highs[i] if highs[i] is not None else closes[i],
                    "l": lows[i] if lows[i] is not None else closes[i],
                    "v": volumes[i] if volumes[i] is not None else 0
                })

        # Sample to max MAX_POINTS
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for j in range(MAX_POINTS):
                idx = min(int(j * step), len(points) - 1)
                sampled.append(points[idx])
            # Always include last point
            if sampled[-1] != points[-1]:
                sampled[-1] = points[-1]
            points = sampled

        # Round floats
        for p in points:
            p["c"] = round(p["c"], 4)
            p["h"] = round(p["h"], 4)
            p["l"] = round(p["l"], 4)
            p["v"] = int(p["v"])

        output[stock_id] = points
        print(f"OK: {stock_id} ({ticker}) -> {len(points)} points (from {len([c for c in closes if c is not None])} raw)")
    except Exception as e:
        print(f"ERR: {stock_id} ({ticker}): {e}")
        output[stock_id] = []

    time.sleep(0.4)

with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(output, f)

print(f"\nDone. Wrote data.json with {len(output)} stocks.")
for k, v in output.items():
    print(f"  {k}: {len(v)} points")
