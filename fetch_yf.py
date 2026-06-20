"""Fetch all stock data using yfinance for better rate limiting."""
import yfinance as yf
import json

TICKERS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

out_dir = '/opt/data/hermes/hbf_dashboard'

# STEP 1: Current prices
print("=== STEP 1: CURRENT PRICES ===")
current = {}
for key, ticker in TICKERS.items():
    try:
        t = yf.Ticker(ticker)
        info = t.info
        hist = t.history(period='5d')
        
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
            prev = float(info.get('previousClose', info.get('regularMarketPreviousClose', 0)))
            if prev == 0 and len(hist) >= 2:
                prev = float(hist['Close'].iloc[-2])
        else:
            price = info.get('currentPrice') or info.get('regularMarketPrice')
            prev = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
        current[key] = {'price': price, 'prev': prev}
        chg = None
        if price and prev and prev != 0:
            chg = round(price - prev, 4)
        print(f"{key}: price={price}, prev={prev}, chg={chg}")
    except Exception as e:
        print(f"{key}: ERROR - {e}")
        current[key] = {'price': None, 'prev': None, 'error': str(e)}

with open(f'{out_dir}/current_prices.json', 'w') as f:
    json.dump(current, f, indent=2)
print(f"\nCurrent prices: {sum(1 for v in current.values() if v.get('price') is not None)}/21 OK")

# STEP 3: 6-month historical data
print("\n=== STEP 3: HISTORICAL DATA ===")
history = {}
for key, ticker in TICKERS.items():
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period='6mo')
        
        points = []
        for idx, row in hist.iterrows():
            points.append({
                't': int(idx.timestamp()),
                'c': round(float(row['Close']), 4),
                'h': round(float(row['High']), 4),
                'l': round(float(row['Low']), 4),
                'v': int(row['Volume'])
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
        
        history[key] = points
        print(f"{key}: {len(points)} points (first={points[0]['c'] if points else 'N/A'}, last={points[-1]['c'] if points else 'N/A'})")
    except Exception as e:
        print(f"{key}: ERROR - {e}")
        history[key] = []

with open(f'{out_dir}/data.json', 'w') as f:
    json.dump(history, f)

print(f"\nHistory: {sum(1 for v in history.values() if len(v) > 0)}/21 stocks have data")
print("DONE")
