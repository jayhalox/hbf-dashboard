import json, urllib.request, ssl, time, sys, os

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

MAX_POINTS = 60
result = {}
errors = []

for sid, ticker in TICKERS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read())
        chart = data['chart']['result'][0]
        ts = chart['timestamp']
        quotes = chart['indicators']['quote'][0]
        opens = quotes.get('open', [])
        closes = quotes.get('close', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        volumes = quotes.get('volume', [])

        points = []
        for i in range(len(ts)):
            c = closes[i] if closes[i] is not None else None
            if c is None:
                continue
            h = highs[i] if highs[i] is not None else c
            l = lows[i] if lows[i] is not None else c
            v = volumes[i] if volumes[i] is not None else 0
            points.append({'t': ts[i], 'c': c, 'h': h, 'l': l, 'v': v})

        # Downsample to max 60 points
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for j in range(MAX_POINTS):
                idx = int(j * step)
                sampled.append(points[idx])
            points = sampled

        result[sid] = points
        print(f"OK  {sid:6s} {ticker:12s} {len(points)} points")
    except Exception as e:
        print(f"ERR {sid:6s} {ticker:12s} {e}")
        errors.append(sid)

outpath = '/opt/data/hermes/hbf_dashboard/data.json'
with open(outpath, 'w') as f:
    json.dump(result, f)

print(f"\nWritten {outpath} — {sum(len(v) for v in result.values())} total points across {len(result)} stocks")
if errors:
    print(f"ERRORS: {errors}")
    sys.exit(1)
