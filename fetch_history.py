import requests
import json
import time
import sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

result = {}

for idx, (key, ticker) in enumerate(TICKERS.items()):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            chart_result = data.get("chart", {}).get("result", [])
            if chart_result:
                r = chart_result[0]
                timestamps = r.get("timestamp", [])
                quotes = r.get("indicators", {}).get("quote", [{}])[0]
                opens = quotes.get("open", [])
                closes = quotes.get("close", [])
                highs = quotes.get("high", [])
                lows = quotes.get("low", [])
                volumes = quotes.get("volume", [])
                
                ohlcv = []
                for i in range(len(timestamps)):
                    c = closes[i] if i < len(closes) and closes[i] is not None else None
                    if c is None:
                        continue
                    ohlcv.append({
                        "t": timestamps[i],
                        "c": round(c, 4),
                        "h": round(highs[i], 4) if i < len(highs) and highs[i] is not None else round(c, 4),
                        "l": round(lows[i], 4) if i < len(lows) and lows[i] is not None else round(c, 4),
                        "v": int(volumes[i]) if i < len(volumes) and volumes[i] is not None else 0
                    })
                
                # Sample to max 60 points
                if len(ohlcv) > 60:
                    step = len(ohlcv) / 60
                    sampled = []
                    for j in range(60):
                        sampled.append(ohlcv[int(j * step)])
                    ohlcv = sampled
                
                result[key] = ohlcv
                print(f"OK: {key} ({ticker}) = {len(ohlcv)} data points", file=sys.stderr)
            else:
                print(f"NO_RESULT: {key} ({ticker})", file=sys.stderr)
                result[key] = []
        else:
            print(f"HTTP_{resp.status_code}: {key} ({ticker})", file=sys.stderr)
            result[key] = []
    except Exception as e:
        print(f"ERR: {key} ({ticker}): {e}", file=sys.stderr)
        result[key] = []
    
    if idx < len(TICKERS) - 1:
        time.sleep(2)

# Write data.json
out_path = "/opt/data/hermes/hbf_dashboard/data.json"
with open(out_path, "w") as f:
    json.dump(result, f, ensure_ascii=False)

total_points = sum(len(v) for v in result.values())
print(f"\nWritten {out_path}: {len(result)} stocks, {total_points} total data points", file=sys.stderr)
print("DONE")
