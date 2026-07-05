import json

# Load current prices and historical data
with open('/opt/data/hermes/hbf_dashboard/results_current.json') as f:
    current = json.load(f)

with open('/opt/data/hermes/hbf_dashboard/data.json') as f:
    hist = json.load(f)

# Generate spark data for each stock (last 13 close values normalized 0-100)
sparks = {}
for sid, points in hist.items():
    if points and len(points) >= 2:
        closes = [p['c'] for p in points[-13:]]
        c_min = min(closes)
        c_max = max(closes)
        rng = c_max - c_min or 1
        sparks[sid] = [round((c - c_min) / rng * 100) for c in closes]
    else:
        sparks[sid] = None

# Format price values for HTML
def fmt_price(sid, val):
    if val is None:
        return 'null'
    # KR and JP use integers
    if sid in ('sk','ss','hanmi','psk','soul','tck','tfe','sol'):
        return str(int(val))
    elif sid in ('tel','adv'):
        return str(int(val))
    elif sid in ('anji','tfme'):
        return str(round(val, 2))
    elif sid in ('asmi','asml'):
        return str(round(val, 2))
    else:  # US stocks
        return str(round(val, 2))

def fmt_chg(sid, val):
    if val is None: return 'null'
    if sid in ('sk','ss','hanmi','psk','soul','tck','tfe','sol','tel','adv'):
        return str(int(val))
    return str(round(val, 2))

def fmt_chgpct(val):
    if val is None: return 'null'
    return str(round(val, 2))

# Build new line for each stock
stock_lines = []
# Order must match HTML
order = ['sk','ss','wdc','mu','amat','tel','asml','asmi','hanmi','psk','entg','soul','tck','anji','tfme','snps','rmbs','ter','adv','tfe','sol']

for sid in order:
    c = current.get(sid)
    spark = sparks.get(sid)
    spark_str = json.dumps(spark) if spark else 'null'
    price = fmt_price(sid, c['price']) if c else 'null'
    prev = fmt_price(sid, c['prev']) if c else 'null'
    chg = fmt_chg(sid, c['chg']) if c else 'null'
    chg_pct = fmt_chgpct(c['chgPct']) if c else 'null'
    print(f"{sid}: price={price}, prev={prev}, chg={chg}, chgPct={chg_pct}, spark={spark_str}")

print("\n=== FULL LINES ===")
for sid in order:
    c = current.get(sid)
    spark = sparks.get(sid)
    spark_str = json.dumps(spark) if spark else 'null'
    price = fmt_price(sid, c['price']) if c else 'null'
    prev = fmt_price(sid, c['prev']) if c else 'null'
    chg = fmt_chg(sid, c['chg']) if c else 'null'
    chg_pct = fmt_chgpct(c['chgPct']) if c else 'null'
    
    # Match the HTML format for each stock
    # Build the full line
    print(f"LINE {sid}: price:{price}, prev:{prev}, chg:{chg}, chgPct:{chg_pct}, spark:{spark_str}")
