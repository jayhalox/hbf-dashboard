import json, urllib.request, time, sys

STOCKS = {
    'sk': ('000660.KS', 'SK hynix', 'KR'),
    'ss': ('005930.KS', 'Samsung', 'KR'),
    'wdc': ('WDC', 'SanDisk / WD', 'US'),
    'mu': ('MU', 'Micron', 'US'),
    'amat': ('AMAT', 'Applied Materials', 'US'),
    'tel': ('8035.T', 'Tokyo Electron', 'JP'),
    'asml': ('ASML', 'ASML', 'NL'),
    'asmi': ('ASM.AS', 'ASM International', 'NL'),
    'hanmi': ('042700.KS', '한미반도체', 'KR'),
    'psk': ('031980.KS', 'PSK Holdings', 'KR'),
    'entg': ('ENTG', 'Entegris', 'US'),
    'soul': ('357780.KS', '솔브레인', 'KR'),
    'tck': ('064760.KS', '티씨케이', 'KR'),
    'anji': ('688019.SS', 'Anji Micro', 'CN'),
    'tfme': ('002156.SZ', 'TFME (通富)', 'CN'),
    'snps': ('SNPS', 'Synopsys', 'US'),
    'rmbs': ('RMBS', 'Rambus', 'US'),
    'ter': ('TER', 'Teradyne', 'US'),
    'adv': ('6857.T', 'Advantest', 'JP'),
    'tfe': ('425420.KS', '티에프이', 'KR'),
    'sol': ('473050.KS', 'SOL AI소부장 ETF', 'KR'),
}

def fetch_current(ticker):
    """Fetch current price + previous close from Yahoo Finance chart API."""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice')
        prev_close = meta.get('previousClose') or meta.get('chartPreviousClose')
        # Fallback: use previous day close from indicators
        if price is None and 'indicators' in result:
            quotes = result['indicators']['quote'][0]
            closes = [c for c in quotes.get('close', []) if c is not None]
            if closes:
                price = closes[-1]
        if prev_close is None and 'indicators' in result:
            quotes = result['indicators']['quote'][0]
            closes = [c for c in quotes.get('close', []) if c is not None]
            if len(closes) >= 2:
                prev_close = closes[-2]
        return price, prev_close
    except Exception as e:
        print(f"  ERROR fetching {ticker}: {e}", file=sys.stderr)
        return None, None

def fetch_historical(ticker):
    """Fetch 6-month daily data, return list of {t, c, h, l, v}."""
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        timestamps = result.get('timestamp', [])
        quotes = result['indicators']['quote'][0]
        opens = quotes.get('open', [])
        closes = quotes.get('close', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        volumes = quotes.get('volume', [])
        points = []
        for i in range(len(timestamps)):
            c = closes[i] if i < len(closes) else None
            if c is None:
                continue
            h = highs[i] if i < len(highs) else c
            l = lows[i] if i < len(lows) else c
            v = volumes[i] if i < len(volumes) else 0
            if v is None:
                v = 0
            if h is None:
                h = c
            if l is None:
                l = c
            points.append({'t': timestamps[i], 'c': c, 'h': h, 'l': l, 'v': v})
        # Downsample to max 60 points
        if len(points) > 60:
            step = len(points) / 60
            sampled = []
            for j in range(60):
                idx = int(j * step)
                sampled.append(points[idx])
            points = sampled
        return points
    except Exception as e:
        print(f"  ERROR historical {ticker}: {e}", file=sys.stderr)
        return []

print("=== STEP 1: Fetching current prices ===")
results = {}
for sid, (ticker, name, country) in STOCKS.items():
    price, prev = fetch_current(ticker)
    chg = round(price - prev, 4) if (price is not None and prev is not None) else None
    chgPct = round((chg / prev) * 100, 2) if (chg is not None and prev and prev != 0) else None
    results[sid] = {'price': price, 'prev': prev, 'chg': chg, 'chgPct': chgPct}
    sign = '+' if (chgPct and chgPct > 0) else ''
    print(f"  {ticker:15s} price={price} prev={prev} chg={chg} chgPct={sign}{chgPct}%")
    time.sleep(0.3)  # Rate limiting

print("\n=== STEP 2: Saving current prices JSON ===")
with open('/opt/data/hermes/hbf_dashboard/prices.json', 'w') as f:
    json.dump(results, f, indent=2)
print("  Saved to prices.json")

print("\n=== STEP 3: Fetching 6-month historical data ===")
historical = {}
for sid, (ticker, name, country) in STOCKS.items():
    pts = fetch_historical(ticker)
    historical[sid] = pts
    print(f"  {ticker:15s} -> {len(pts)} data points")
    time.sleep(0.3)

print("\n=== Saving data.json ===")
with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(historical, f)
print("  Saved data.json")

print("\n=== DONE ===")
