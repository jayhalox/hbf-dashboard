import requests, json, time, sys

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

TICKERS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

def fetch_current(ticker):
    """Fetch current price from 5-day data"""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d'
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        result = data['chart']['result'][0]
        meta = result['meta']
        quotes = result['indicators']['quote'][0]
        timestamps = result['timestamp']
        
        # Get the most recent close
        closes = [v for v in quotes['close'] if v is not None]
        prev_close = meta.get('chartPreviousClose') or meta.get('previousClose')
        current = meta.get('regularMarketPrice') or (closes[-1] if closes else None)
        
        if current is None and closes:
            current = closes[-1]
        if prev_close is None and len(closes) >= 2:
            prev_close = closes[-2]
        
        return {
            'price': current,
            'prev': prev_close,
            'timestamps': timestamps,
            'closes': closes,
            'highs': [h for h in quotes['high'] if h is not None],
            'lows': [l for l in quotes['low'] if l is not None],
            'volumes': [v for v in quotes['volume'] if v is not None],
        }
    except Exception as e:
        return {'error': str(e), 'price': None, 'prev': None}

def fetch_history(ticker):
    """Fetch 6-month historical data"""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo'
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        result = data['chart']['result'][0]
        quotes = result['indicators']['quote'][0]
        timestamps = result['timestamp']
        
        points = []
        for i in range(len(timestamps)):
            c = quotes['close'][i]
            if c is None:
                continue
            points.append({
                't': timestamps[i],
                'c': c,
                'h': quotes['high'][i] if quotes['high'][i] is not None else c,
                'l': quotes['low'][i] if quotes['low'][i] is not None else c,
                'v': quotes['volume'][i] if quotes['volume'][i] is not None else 0
            })
        
        # Sample to max 60 points
        if len(points) > 60:
            step = len(points) / 60
            sampled = []
            for i in range(60):
                idx = int(i * step)
                if idx < len(points):
                    sampled.append(points[idx])
            points = sampled
        
        return points
    except Exception as e:
        return None

# Step 1: Current prices
print("=== STEP 1: CURRENT PRICES ===")
current_data = {}
for key, ticker in TICKERS.items():
    print(f"Fetching {key} ({ticker})...", end=" ", flush=True)
    result = fetch_current(ticker)
    current_data[key] = result
    if result.get('error'):
        print(f"ERROR: {result['error']}")
    else:
        chg = None
        if result['price'] is not None and result['prev'] is not None:
            chg = round(result['price'] - result['prev'], 4)
        print(f"price={result['price']}, prev={result['prev']}, chg={chg}")
    time.sleep(0.15)

with open('/opt/data/hermes/hbf_dashboard/current_prices.json', 'w') as f:
    json.dump(current_data, f, indent=2)

print("\nCurrent prices saved to current_prices.json")

# Step 3: Historical data
print("\n=== STEP 3: HISTORICAL DATA ===")
history_data = {}
for key, ticker in TICKERS.items():
    print(f"Fetching history {key} ({ticker})...", end=" ", flush=True)
    points = fetch_history(ticker)
    if points:
        history_data[key] = points
        print(f"{len(points)} points (first={points[0]['c']}, last={points[-1]['c']})")
    else:
        history_data[key] = []
        print("FAILED")
    time.sleep(0.15)

with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(history_data, f)

print("\nHistorical data saved to data.json")
print("DONE")
