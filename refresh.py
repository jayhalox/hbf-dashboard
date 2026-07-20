#!/usr/bin/env python3
"""HBF Dashboard daily refresh: fetch prices, update HTML, generate data.json"""
import json, time, re, math, urllib.request, sys
from datetime import datetime, timezone

STOCKS_CONFIG = [
    ('sk',    '000660.KS',  'KR'),  ('ss',    '005930.KS',  'KR'),
    ('wdc',   'WDC',        'US'),  ('mu',    'MU',          'US'),
    ('amat',  'AMAT',       'US'),  ('tel',   '8035.T',      'JP'),
    ('asml',  'ASML',       'NL'),  ('asmi',  'ASM.AS',      'NL'),
    ('hanmi', '042700.KS',  'KR'),  ('psk',   '031980.KS',   'KR'),
    ('entg',  'ENTG',       'US'),  ('soul',  '357780.KS',   'KR'),
    ('tck',   '064760.KS',  'KR'),  ('anji',  '688019.SS',   'CN'),
    ('tfme',  '002156.SZ',  'CN'),  ('snps',  'SNPS',        'US'),
    ('rmbs',  'RMBS',       'US'),  ('ter',   'TER',         'US'),
    ('adv',   '6857.T',     'JP'),  ('tfe',   '425420.KS',   'KR'),
    ('sol',   '473050.KS',  'KR'),
]

def fetch_current_price(ticker):
    """Fetch current price and previous close from Yahoo Finance chart API."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        result = data['chart']['result'][0]
        meta = result['meta']
        price = meta.get('regularMarketPrice')
        prev = meta.get('previousClose') or meta.get('chartPreviousClose')
        if price is None:
            # Try to get from quotes
            quotes = result.get('indicators', {}).get('quote', [{}])[0]
            closes = [x for x in quotes.get('close', []) if x is not None]
            if closes:
                price = closes[-1]
                if len(closes) >= 2:
                    prev = closes[-2]
        return price, prev
    except Exception as e:
        print(f"  ERROR fetching {ticker}: {e}", file=sys.stderr)
        return None, None

def fetch_6mo_data(ticker, max_points=60):
    """Fetch 6-month historical data."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        result = data['chart']['result'][0]
        timestamps = result.get('timestamp', [])
        quotes = result.get('indicators', {}).get('quote', [{}])[0]
        opens = quotes.get('open', [])
        highs = quotes.get('high', [])
        lows = quotes.get('low', [])
        closes = quotes.get('close', [])
        volumes = quotes.get('volume', [])
        
        points = []
        for i, t in enumerate(timestamps):
            c = closes[i] if i < len(closes) and closes[i] is not None else None
            if c is None:
                continue
            h = highs[i] if i < len(highs) and highs[i] is not None else c
            l = lows[i] if i < len(lows) and lows[i] is not None else c
            v = volumes[i] if i < len(volumes) and volumes[i] is not None else 0
            points.append({"t": t, "c": c, "h": h, "l": l, "v": v})
        
        # Sample down to max_points
        if len(points) > max_points:
            step = len(points) / max_points
            sampled = [points[0]]
            for j in range(1, max_points - 1):
                idx = int(j * step)
                if idx < len(points):
                    sampled.append(points[idx])
            sampled.append(points[-1])
            points = sampled
        
        return points
    except Exception as e:
        print(f"  ERROR 6mo data {ticker}: {e}", file=sys.stderr)
        return []

print(f"📊 HBF Dashboard Refresh — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# STEP 1: Fetch current prices
print("\n📈 STEP 1: Fetching current prices...")
prices = {}
for stock_id, ticker, country in STOCKS_CONFIG:
    price, prev = fetch_current_price(ticker)
    prices[stock_id] = (price, prev)
    if price:
        print(f"  {stock_id:6s} ({ticker:12s}): price={price}, prev={prev}")
    else:
        print(f"  {stock_id:6s} ({ticker:12s}): FAILED")
    time.sleep(0.3)  # Rate limit

# STEP 2: Update index.html
print("\n📝 STEP 2: Updating index.html...")
html_path = '/opt/data/hermes/hbf_dashboard/index.html'
with open(html_path, 'r') as f:
    html = f.read()

# Extract the STOCKS array
pattern = r'(const STOCKS=\[.*?\n\];)'
match = re.search(pattern, html, re.DOTALL)
if not match:
    print("  ERROR: Could not find STOCKS array!", file=sys.stderr)
    sys.exit(1)

old_stocks_block = match.group(0)
# Parse individual stock lines
stock_pattern = r"\{id:'(\w+)',name:'([^']*)',ticker:'([^']*)',country:'(\w+)',flag:'([^']*)',step:'(\w+)',price:([^,]*),prev:([^,]*),chg:([^,]*),chgPct:([^,]*),spark:(\[[^\]]*\])[^}]*\}"

def update_stock_line(line, stock_map):
    m = re.search(stock_pattern, line)
    if not m:
        return line
    sid = m.group(1)
    if sid not in stock_map:
        return line
    price, prev = stock_map[sid]
    if price is None:
        return line  # Keep existing values if fetch failed
    
    # Calculate chg and chgPct
    if prev and prev != 0:
        chg = round(price - prev, 2)
        chgPct = round((price - prev) / prev * 100, 2)
    else:
        chg = 0
        chgPct = 0
    
    # Replace the values
    old_sub = re.search(r"price:([^,]*),prev:([^,]*),chg:([^,]*),chgPct:([^,]*),", line)
    if old_sub:
        repl = f"price:{price},prev:{prev},chg:{chg},chgPct:{chgPct},"
        line = line[:old_sub.start()] + repl + line[old_sub.end():]
    
    return line

lines = old_stocks_block.split('\n')
new_lines = []
for line in lines:
    new_lines.append(update_stock_line(line, prices))
new_stocks_block = '\n'.join(new_lines)

html = html.replace(old_stocks_block, new_stocks_block)

# Update the timestamp
now_str = datetime.now().strftime('%Y-%m-%d %H:%M KST')
html = re.sub(r'<span class="update-time">[^<]*</span>', 
              f'<span class="update-time">{now_str}</span>', html)

with open(html_path, 'w') as f:
    f.write(html)
print("  ✅ index.html updated")

# STEP 3: Fetch 6-month historical data
print("\n📊 STEP 3: Fetching 6-month historical data...")
hist_data = {}
for stock_id, ticker, country in STOCKS_CONFIG:
    print(f"  Fetching {stock_id} ({ticker})...")
    points = fetch_6mo_data(ticker)
    hist_data[stock_id] = points
    print(f"    Got {len(points)} data points")
    time.sleep(0.4)  # Rate limit

# Write data.json
data_path = '/opt/data/hermes/hbf_dashboard/data.json'
with open(data_path, 'w') as f:
    json.dump(hist_data, f)
print(f"  ✅ data.json written with {sum(len(v) for v in hist_data.values())} total data points")

print("\n" + "=" * 60)
print("✅ ALL DONE — Ready for git commit")
print(f"   Updated {len([s for s, p in prices.items() if p[0] is not None])}/{len(prices)} stocks")
