import json, os, glob

raw_dir = '/opt/data/hermes/hbf_dashboard/raw_responses'
results = {}

for fpath in sorted(glob.glob(f'{raw_dir}/*.json')):
    key = os.path.basename(fpath).replace('.json', '')
    with open(fpath) as f:
        raw = f.read()
    
    if len(raw) < 100:
        results[key] = {'price': None, 'prev': None, 'error': 'rate_limited'}
        continue
    
    try:
        data = json.loads(raw)
        meta = data['chart']['result'][0]['meta']
        price = meta.get('regularMarketPrice')
        prev = meta.get('chartPreviousClose') or meta.get('previousClose')
        results[key] = {'price': price, 'prev': prev}
        chg = None
        if price is not None and prev is not None and prev != 0:
            chg = round(price - prev, 6)
        print(f"{key}: price={price}, prev={prev}, chg={chg}")
    except Exception as e:
        results[key] = {'price': None, 'prev': None, 'error': str(e)}
        print(f"{key}: PARSE ERROR: {e}")

with open('/opt/data/hermes/hbf_dashboard/current_prices.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nTotal: {len(results)} stocks")
print(f"Success: {sum(1 for v in results.values() if v.get('price') is not None)}")
print(f"Failed: {sum(1 for v in results.values() if v.get('price') is None)}")

# List failed ones for retry
failed = [k for k,v in results.items() if v.get('price') is None]
if failed:
    print(f"Need retry: {', '.join(failed)}")
