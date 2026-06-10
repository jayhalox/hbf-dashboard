import json
import urllib.request
import ssl
import time

STOCKS = {
    'sk': '000660.KS',
    'ss': '005930.KS',
    'wdc': 'WDC',
    'mu': 'MU',
    'amat': 'AMAT',
    'tel': '8035.T',
    'asml': 'ASML',
    'asmi': 'ASM',
    'hanmi': '042700.KS',
    'psk': '031980.KS',
    'entg': 'ENTG',
    'soul': '357780.KS',
    'tck': '064760.KS',
    'anji': '688019.SS',
    'tfme': '002156.SZ',
    'snps': 'SNPS',
    'rmbs': 'RMBS',
    'ter': 'TER',
    'adv': '6857.T',
    'tfe': '425420.KS',
    'sol': '473050.KS',
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

results = {}
for sid, ticker in STOCKS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        meta = result['meta']
        quotes = result['indicators']['quote'][0]
        timestamps = result.get('timestamp', [])

        # Current price = meta.regularMarketPrice, previous close = meta.previousClose
        price = meta.get('regularMarketPrice', None)
        prev_close = meta.get('previousClose', None)
        # Also get today's close from the latest quote
        closes = quotes.get('close', [])
        closes = [c for c in closes if c is not None]

        chg = None
        chgPct = None
        if price is not None and prev_close is not None and prev_close != 0:
            chg = round(price - prev_close, 2)
            chgPct = round((price - prev_close) / prev_close * 100, 2)

        results[sid] = {
            'ticker': ticker,
            'price': price,
            'prev': prev_close,
            'chg': chg,
            'chgPct': chgPct,
            'closes': closes[-5:] if len(closes) >= 5 else closes,
        }
        print(f"OK {sid}: price={price}, prev={prev_close}, chg={chg}, chgPct={chgPct}")
    except Exception as e:
        print(f"ERR {sid}: {e}")
        results[sid] = {'ticker': ticker, 'price': None, 'prev': None, 'chg': None, 'chgPct': None, 'closes': []}

    time.sleep(0.3)  # Rate limit

with open('/opt/data/hermes/hbf_dashboard/prices.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n=== ALL DONE ===")
print(json.dumps(results, indent=2))
