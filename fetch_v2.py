import requests
import json
import time
import os

TICKERS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
})

# First, get Yahoo cookies
print("Getting Yahoo cookies...")
try:
    session.get('https://fc.yahoo.com/', timeout=15)
    print(f"Cookies: {dict(session.cookies)}")
except Exception as e:
    print(f"Cookie fetch warning: {e}")

# Also try yahoo.com directly
try:
    session.get('https://finance.yahoo.com/', timeout=15)
    print(f"Cookies after finance: {dict(session.cookies)}")
except Exception as e:
    print(f"Finance cookie warning: {e}")

results = {}
out_dir = '/opt/data/hermes/hbf_dashboard'

for key, ticker in TICKERS.items():
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d'
    print(f"Fetching {key} ({ticker})...", end=" ", flush=True)
    
    try:
        r = session.get(url, timeout=20)
        # Save raw response
        raw_path = f'{out_dir}/_raw_{key}.json'
        with open(raw_path, 'w') as f:
            f.write(r.text)
        
        if r.status_code != 200:
            print(f"HTTP {r.status_code}")
            results[key] = {'price': None, 'prev': None, 'error': f'HTTP {r.status_code}'}
            continue
            
        data = r.json()
        meta = data['chart']['result'][0]['meta']
        
        price = meta.get('regularMarketPrice')
        prev = meta.get('chartPreviousClose') or meta.get('previousClose')
        
        results[key] = {'price': price, 'prev': prev}
        
        chg = None
        if price is not None and prev is not None and prev != 0:
            chg = round(price - prev, 6)
        print(f"price={price}, prev={prev}, chg={chg}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        results[key] = {'price': None, 'prev': None, 'error': str(e)}
    
    time.sleep(0.3)

# Save results
with open(f'{out_dir}/current_prices.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n=== SUMMARY ===")
for key, data in results.items():
    p = data.get('price')
    pr = data.get('prev')
    if p is not None and pr is not None:
        chg = round(p - pr, 6)
        pct = round((chg / pr) * 100, 2) if pr != 0 else 0
        print(f"{key}: {p} (prev={pr}, chg={chg}, chgPct={pct}%)")
    else:
        print(f"{key}: FAILED - {data.get('error', 'unknown')}")

print("DONE")
