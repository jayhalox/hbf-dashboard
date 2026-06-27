import json, urllib.request, time, sys, math

tickers = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

MAX_POINTS = 60
result = {}

for key, ticker in tickers.items():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        
        r = data["chart"]["result"][0]
        timestamps = r["timestamp"]
        quotes = r["indicators"]["quote"][0]
        opens = quotes["open"]
        highs = quotes["high"]
        lows = quotes["low"]
        closes = quotes["close"]
        volumes = quotes["volume"]
        
        points = []
        for i in range(len(timestamps)):
            c = closes[i] if closes[i] is not None else (opens[i] or 0)
            h = highs[i] if highs[i] is not None else c
            l = lows[i] if lows[i] is not None else c
            v = volumes[i] if volumes[i] is not None else 0
            points.append({"t": timestamps[i], "c": c, "h": h, "l": l, "v": v})
        
        # Sample to MAX_POINTS
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for i in range(MAX_POINTS):
                idx = min(int(i * step), len(points) - 1)
                sampled.append(points[idx])
            # Always include last point
            sampled[-1] = points[-1]
            points = sampled
        
        result[key] = points
        print(f"OK {key:6s} {ticker:12s} {len(points)} points")
    except Exception as e:
        print(f"ERR {key:6s} {ticker:12s} {e}")
        result[key] = []

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(result, f)

print(f"\nSaved data.json with {sum(1 for v in result.values() if v)} stocks")
