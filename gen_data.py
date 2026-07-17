import json, urllib.request, time
from datetime import datetime

TICKERS = [
    ("sk", "000660.KS"), ("ss", "005930.KS"), ("wdc", "WDC"), ("mu", "MU"),
    ("amat", "AMAT"), ("tel", "8035.T"), ("asml", "ASML"), ("asmi", "ASM.AS"),
    ("hanmi", "042700.KS"), ("psk", "031980.KS"), ("entg", "ENTG"),
    ("soul", "357780.KS"), ("tck", "064760.KS"), ("anji", "688019.SS"),
    ("tfme", "002156.SZ"), ("snps", "SNPS"), ("rmbs", "RMBS"), ("ter", "TER"),
    ("adv", "6857.T"), ("tfe", "425420.KS"), ("sol", "473050.KS"),
]

result = {}
for sid, ticker in TICKERS:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        d = data["chart"]["result"][0]
        quotes = d["indicators"]["quote"][0]
        timestamps = d["timestamp"]
        
        points = []
        for i, ts in enumerate(timestamps):
            c = quotes["close"][i]
            if c is None:
                continue
            h = quotes["high"][i]
            l = quotes["low"][i]
            v = quotes["volume"][i]
            points.append({"t": ts, "c": c, "h": h, "l": l, "v": v if v else 0})
        
        # Sample to max 60 points
        if len(points) > 60:
            step = len(points) / 60
            sampled = []
            for i in range(60):
                idx = int(i * step)
                sampled.append(points[idx])
            points = sampled
        
        result[sid] = points
        print(f"OK: {sid} ({ticker}) - {len(points)} points")
    except Exception as e:
        print(f"FAIL: {sid} ({ticker}): {e}")

with open("/opt/data/hermes/hbf_dashboard/data.json", "w") as f:
    json.dump(result, f)

print(f"\nDone. Wrote data.json with {len(result)} stocks.")
ts = datetime.now().strftime("%Y-%m-%d %H:%M KST")
print(f"Timestamp: {ts}")
with open("/opt/data/hermes/hbf_dashboard/last_update.txt", "w") as f:
    f.write(ts)
