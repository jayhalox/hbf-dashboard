import json, urllib.request, sys

TICKERS = {
    "sk": "000660.KS", "ss": "005930.KS", "wdc": "WDC", "mu": "MU",
    "amat": "AMAT", "tel": "8035.T", "asml": "ASML", "asmi": "ASM",
    "hanmi": "042700.KS", "psk": "031980.KS", "entg": "ENTG",
    "soul": "357780.KS", "tck": "064760.KS", "anji": "688019.SS",
    "tfme": "002156.SZ", "snps": "SNPS", "rmbs": "RMBS", "ter": "TER",
    "adv": "6857.T", "tfe": "425420.KS", "sol": "473050.KS"
}

for sid, ticker in TICKERS.items():
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read())["chart"]["result"][0]
        meta = d["meta"]
        price = meta["regularMarketPrice"]
        prev = meta["chartPreviousClose"]
        chg = price - prev
        chg_pct = (chg / prev) * 100
        print(f"{sid}: price={price:.2f}, prev={prev:.2f}, chg={chg:.2f}, chgPct={chg_pct:.2f}")
    except Exception as e:
        print(f"{sid}: ERROR - {e}", file=sys.stderr)
