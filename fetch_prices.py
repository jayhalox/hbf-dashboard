import json, urllib.request, time, sys, math
from datetime import datetime

stocks = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM.AS',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

results_current = {}
results_hist = {}

for sid, ticker in stocks.items():
    try:
        # Current price: 5d range
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        chart = data['chart']['result'][0]
        meta = chart['meta']
        quotes = chart['indicators']['quote'][0]
        
        # Get close prices
        timestamps = chart['timestamp']
        closes = quotes['close']
        highs = quotes['high']
        lows = quotes['low']
        volumes = quotes['volume']
        
        # Filter out None values
        valid = [(t, c, h, l, v) for t, c, h, l, v in zip(timestamps, closes, highs, lows, volumes) if c is not None]
        
        if len(valid) >= 2:
            prev_close = valid[-2][1]
            curr_close = valid[-1][1]
            chg = round(curr_close - prev_close, 2)
            chg_pct = round((chg / prev_close) * 100, 2)
        elif len(valid) == 1:
            prev_close = meta.get('previousClose', valid[0][1])
            curr_close = valid[0][1]
            chg = round(curr_close - prev_close, 2)
            chg_pct = round((chg / prev_close) * 100, 2) if prev_close else 0
        else:
            prev_close = meta.get('previousClose', 0)
            curr_close = meta.get('regularMarketPrice', prev_close)
            chg = round(curr_close - prev_close, 2) if prev_close else 0
            chg_pct = round((chg / prev_close) * 100, 2) if prev_close else 0
        
        results_current[sid] = {
            'price': curr_close, 'prev': prev_close,
            'chg': chg, 'chgPct': chg_pct
        }
        print(f"[OK] {sid} ({ticker}): price={curr_close}, prev={prev_close}, chg={chg}, chgPct={chg_pct}%")
    except Exception as e:
        print(f"[ERR] {sid} ({ticker}): {e}", file=sys.stderr)
        results_current[sid] = None

    try:
        # 6-month historical: 6mo range
        url_hist = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
        req = urllib.request.Request(url_hist, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data_hist = json.loads(resp.read().decode())
        
        chart_hist = data_hist['chart']['result'][0]
        timestamps = chart_hist['timestamp']
        quotes = chart_hist['indicators']['quote'][0]
        closes = quotes['close']
        highs = quotes['high']
        lows = quotes['low']
        volumes = quotes['volume']
        
        points = [{'t': t, 'c': c, 'h': h, 'l': l, 'v': v}
                  for t, c, h, l, v in zip(timestamps, closes, highs, lows, volumes)
                  if c is not None]
        
        # Sample to max 60 points
        if len(points) > 60:
            step = len(points) / 60
            sampled = [points[math.floor(i * step)] for i in range(60)]
            # Ensure last point is included
            if sampled[-1] != points[-1]:
                sampled[-1] = points[-1]
            points = sampled
        
        results_hist[sid] = points
        print(f"[HIST OK] {sid}: {len(points)} points (from {len([p for p in zip(timestamps, closes) if p[1] is not None])} raw)")
    except Exception as e:
        print(f"[HIST ERR] {sid}: {e}", file=sys.stderr)
        results_hist[sid] = []

    time.sleep(0.3)  # Rate limit

# Output results
print("\n=== CURRENT PRICES ===")
print(json.dumps(results_current, indent=2))

print("\n=== HISTORICAL DATA SUMMARY ===")
for sid, points in results_hist.items():
    if points:
        print(f"{sid}: {len(points)} points, {points[0]['t']} to {points[-1]['t']}")

# Write outputs
with open('/opt/data/hermes/hbf_dashboard/results_current.json', 'w') as f:
    json.dump(results_current, f, indent=2)
with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(results_hist, f)
print("\nFiles written: results_current.json, data.json")
