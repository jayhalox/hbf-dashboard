import json, urllib.request, time, math

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM.AS",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

MAX_POINTS = 60
output = {}

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read())
        result = data['chart']['result'][0]
        ts = result['timestamp']
        quote = result['indicators']['quote'][0]
        opens = quote['open']
        highs = quote['high']
        lows = quote['low']
        closes = quote['close']
        volumes = quote['volume']

        points = []
        for i in range(len(ts)):
            c = closes[i]
            if c is None:
                continue
            h = highs[i] if highs[i] is not None else c
            l = lows[i] if lows[i] is not None else c
            v = volumes[i] if volumes[i] is not None else 0
            points.append({"t": ts[i], "c": round(c, 2), "h": round(h, 2), "l": round(l, 2), "v": v})

        # Downsample to MAX_POINTS if needed
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for j in range(MAX_POINTS):
                idx = int(j * step)
                # Take a small window around this index
                start = max(0, idx - 1)
                end = min(len(points), idx + 2)
                window = points[start:end]
                sampled.append({
                    "t": points[idx]["t"],
                    "c": round(sum(p["c"] for p in window) / len(window), 2),
                    "h": max(p["h"] for p in window),
                    "l": min(p["l"] for p in window),
                    "v": sum(p["v"] for p in window)
                })
            points = sampled

        output[sid] = points
        print(f"{sid} ({ticker}): {len(points)} points")
    except Exception as e:
        print(f"{sid} ({ticker}): ERROR - {e}")
        output[sid] = []

    time.sleep(0.3)

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(output, f)

total = sum(1 for v in output.values() if v)
print(f"\n--- DONE ---")
print(f"Stocks with data: {total} / {len(TICKERS)}")
print(f"Total data points: {sum(len(v) for v in output.values())}")
