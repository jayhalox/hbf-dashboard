import json
import urllib.request
import ssl
import time
import math

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

MAX_POINTS = 60

result = {}
for sid, ticker in STOCKS.items():
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode())
        
        chart_result = data['chart']['result'][0]
        timestamps = chart_result.get('timestamp', [])
        quotes = chart_result['indicators']['quote'][0]
        opens = quotes.get('open', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        closes = quotes.get('close', [])
        volumes = quotes.get('volume', [])

        # Build OHLCV data
        ohlcv = []
        for i in range(len(timestamps)):
            c = closes[i] if i < len(closes) and closes[i] is not None else None
            if c is None:
                continue
            ohlcv.append({
                't': timestamps[i],
                'c': round(c, 4),
                'h': round(highs[i], 4) if i < len(highs) and highs[i] is not None else round(c, 4),
                'l': round(lows[i], 4) if i < len(lows) and lows[i] is not None else round(c, 4),
                'v': volumes[i] if i < len(volumes) and volumes[i] is not None else 0,
            })

        # Downsample to max 60 points
        if len(ohlcv) > MAX_POINTS:
            step = len(ohlcv) / MAX_POINTS
            sampled = []
            for i in range(MAX_POINTS):
                idx = int(i * step)
                sampled.append(ohlcv[idx])
            # Always include last point
            sampled[-1] = ohlcv[-1]
            ohlcv = sampled

        result[sid] = ohlcv
        print(f"OK {sid}: {len(ohlcv)} points")
    except Exception as e:
        print(f"ERR {sid}: {e}")
        result[sid] = []

    time.sleep(0.3)

with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(result, f, indent=2)

print(f"\n=== data.json written with {sum(len(v) for v in result.values())} total points ===")
