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

results = {}

for idx, (key, ticker) in enumerate(TICKERS.items()):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("chart", {}).get("result", [])
            if result:
                meta = result[0].get("meta", {})
                quotes = result[0].get("indicators", {}).get("quote", [{}])[0]
                closes = [c for c in quotes.get("close", []) if c is not None]
                timestamps = result[0].get("timestamp", [])
                
                price = closes[-1] if closes else meta.get("regularMarketPrice")
                
                # Previous close: use second-to-last close or meta.chartPreviousClose
                prev = None
                if len(closes) >= 2:
                    prev = closes[-2]
                elif meta.get("chartPreviousClose"):
                    prev = meta["chartPreviousClose"]
                elif meta.get("previousClose"):
                    prev = meta["previousClose"]
                
                results[key] = {
                    "ticker": ticker,
                    "price": price,
                    "prev": prev,
                    "all_closes": closes,
                    "timestamp": timestamps[-1] if timestamps else None
                }
                print(f"OK: {key} ({ticker}) price={price} prev={prev}", file=sys.stderr)
            else:
                print(f"NO_RESULT: {key} ({ticker})", file=sys.stderr)
                results[key] = {"ticker": ticker, "price": None, "prev": None}
        else:
            print(f"HTTP_{resp.status_code}: {key} ({ticker})", file=sys.stderr)
            results[key] = {"ticker": ticker, "price": None, "prev": None}
    except Exception as e:
        print(f"ERR: {key} ({ticker}): {e}", file=sys.stderr)
        results[key] = {"ticker": ticker, "price": None, "prev": None}
    
    if idx < len(TICKERS) - 1:
        time.sleep(1.5)

print(json.dumps(results, indent=2, ensure_ascii=False))
