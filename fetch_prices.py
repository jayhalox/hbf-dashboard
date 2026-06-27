import json, urllib.request, sys

tickers = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

results = {}
for key, ticker in tickers.items():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        r = data["chart"]["result"][0]
        meta = r["meta"]
        price = meta["regularMarketPrice"]
        prev = meta.get("previousClose", price)
        results[key] = {"price": price, "prev": prev}
        print(f"OK {key:6s} {ticker:12s} price={price:>12.2f} prev={prev:>12.2f}")
    except Exception as e:
        print(f"ERR {key:6s} {ticker:12s} {e}")
        results[key] = {"price": None, "prev": None, "error": str(e)}

with open("/opt/data/hermes/hbf_dashboard/prices.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. Saved to prices.json")
