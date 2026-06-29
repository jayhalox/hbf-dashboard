import json
import urllib.request
import time
import sys
import math

STOCKS = [
    ('sk', '000660.KS'),
    ('ss', '005930.KS'),
    ('wdc', 'WDC'),
    ('mu', 'MU'),
    ('amat', 'AMAT'),
    ('tel', '8035.T'),
    ('asml', 'ASML'),
    ('asmi', 'ASM'),
    ('hanmi', '042700.KS'),
    ('psk', '031980.KS'),
    ('entg', 'ENTG'),
    ('soul', '357780.KS'),
    ('tck', '064760.KS'),
    ('anji', '688019.SS'),
    ('tfme', '002156.SZ'),
    ('snps', 'SNPS'),
    ('rmbs', 'RMBS'),
    ('ter', 'TER'),
    ('adv', '6857.T'),
    ('tfe', '425420.KS'),
    ('sol', '473050.KS'),
]

def fetch_chart(ticker, range_str="5d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range={range_str}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        meta = result['meta']
        quotes = result['indicators']['quote'][0]
        timestamps = result.get('timestamp', [])
        closes = quotes.get('close', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        volumes = quotes.get('volume', [])
        return {
            'price': meta.get('regularMarketPrice'),
            'prev': meta.get('previousClose') or meta.get('chartPreviousClose'),
            'high': meta.get('regularMarketDayHigh'),
            'low': meta.get('regularMarketDayLow'),
            'quotes': list(zip(timestamps, closes, highs, lows, volumes))
        }
    except Exception as e:
        print(f"ERROR fetching {ticker}: {e}", file=sys.stderr)
        return None

# STEP 1: Fetch current prices (5d range)
print("=== STEP 1: Current Prices ===")
prices = {}
for stock_id, ticker in STOCKS:
    print(f"Fetching {stock_id} ({ticker})...", end=" ", flush=True)
    data = fetch_chart(ticker, "5d")
    if data and data['price'] is not None:
        prices[stock_id] = data
        chg = data['price'] - (data['prev'] or data['price'])
        pct = (chg / data['prev'] * 100) if data['prev'] and data['prev'] != 0 else 0
        print(f"Price={data['price']}, Prev={data['prev']}, Chg={chg:.2f}, ChgPct={pct:.2f}%")
    else:
        print("NO DATA")
    time.sleep(0.4)  # rate limit

# Write price summary
with open('/opt/data/hermes/hbf_dashboard/prices.json', 'w') as f:
    json.dump(prices, f, indent=2, default=str)

print("\n=== Price fetch complete ===")
print(json.dumps({k: {'price': v['price'], 'prev': v['prev']} for k, v in prices.items()}, indent=2, default=str))

# STEP 3: Fetch 6-month historical data
print("\n=== STEP 3: 6-Month Historical Data ===")
historical = {}
for stock_id, ticker in STOCKS:
    print(f"Fetching {stock_id} ({ticker}) 6mo...", end=" ", flush=True)
    data = fetch_chart(ticker, "6mo")
    if data and data['quotes']:
        quotes = data['quotes']
        # Clean None values
        cleaned = []
        for t, c, h, l, v in quotes:
            if c is not None:
                cleaned.append({
                    't': t,
                    'c': round(c, 4),
                    'h': round(h, 4) if h is not None else round(c, 4),
                    'l': round(l, 4) if l is not None else round(c, 4),
                    'v': int(v) if v is not None else 0
                })
        # Sample to max 60 points
        if len(cleaned) > 60:
            step = len(cleaned) / 60
            sampled = [cleaned[math.floor(i * step)] for i in range(60)]
        else:
            sampled = cleaned
        historical[stock_id] = sampled
        print(f"{len(cleaned)} raw -> {len(sampled)} sampled")
    else:
        print("NO DATA")
    time.sleep(0.4)

with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(historical, f, indent=2)

print("\n=== Historical data written to data.json ===")
print(f"Stocks in data.json: {list(historical.keys())}")
