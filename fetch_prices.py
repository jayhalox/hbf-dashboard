import json, urllib.request, ssl, time

# Disable SSL verification for the API call
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

TICKERS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

results = {}

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            data = json.loads(resp.read())
        chart = data['chart']['result'][0]
        meta = chart['meta']
        quotes = chart['indicators']['quote'][0]
        ts = chart['timestamp']

        prev_close = meta.get('chartPreviousClose', meta.get('previousClose', 0))
        current_price = meta.get('regularMarketPrice', 0)
        if current_price == 0 and quotes['close']:
            current_price = quotes['close'][-1]

        chg = current_price - prev_close
        chg_pct = (chg / prev_close * 100) if prev_close else 0

        results[sid] = {
            'ticker': ticker,
            'price': round(current_price, 2),
            'prev': round(prev_close, 2),
            'chg': round(chg, 2),
            'chgPct': round(chg_pct, 2)
        }
        print(f"OK  {sid:6s} {ticker:12s} price={current_price:>12.2f} prev={prev_close:>12.2f} chg={chg:>+10.2f} ({chg_pct:>+6.2f}%)")
    except Exception as e:
        print(f"ERR {sid:6s} {ticker:12s} {e}")
        results[sid] = {'ticker': ticker, 'error': str(e)}

print("\n--- JSON ---")
print(json.dumps(results, indent=2))
