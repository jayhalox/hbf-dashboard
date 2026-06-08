import json, urllib.request, sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

MAX_POINTS = 60

result = {}

for sid, ticker in TICKERS.items():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read())["chart"]["result"][0]
        
        timestamps = d["timestamp"]
        quote = d["indicators"]["quote"][0]
        opens = quote.get("open", [])
        highs = quote.get("high", [])
        lows = quote.get("low", [])
        closes = quote.get("close", [])
        volumes = quote.get("volume", [])
        
        points = []
        for i in range(len(timestamps)):
            c = closes[i] if i < len(closes) and closes[i] is not None else None
            if c is None:
                continue
            h = highs[i] if i < len(highs) and highs[i] is not None else c
            l = lows[i] if i < len(lows) and lows[i] is not None else c
            v = int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0
            points.append({"t": timestamps[i], "c": c, "h": h, "l": l, "v": v})
        
        # Sample to max 60 points
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for j in range(MAX_POINTS):
                idx = min(int(j * step), len(points) - 1)
                sampled.append(points[idx])
            points = sampled
        
        result[sid] = points
        print(f"{sid}: {len(points)} points", file=sys.stderr)
    except Exception as e:
        print(f"{sid}: ERROR - {e}", file=sys.stderr)
        result[sid] = []

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(result, f)

print("Done. File written to /opt/data/hermes/hbf_dashboard/data.json")
