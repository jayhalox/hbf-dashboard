import re

# New values from API fetch
new_data = {
    'sk':   {'price': 1913000, 'prev': 2076000, 'chg': -163000, 'chgPct': -7.85},
    'ss':   {'price': 263000,  'prev': 277500,  'chg': -14500,  'chgPct': -5.23},
    'wdc':  {'price': 563.32,  'prev': 532.10,  'chg': 31.22,   'chgPct': 5.87},
    'mu':   {'price': 983.12,  'prev': 938.38,  'chg': 44.74,   'chgPct': 4.77},
    'amat': {'price': 595.70,  'prev': 554.50,  'chg': 41.20,   'chgPct': 7.43},
    'tel':  {'price': 71130,   'prev': 71060,   'chg': 70,      'chgPct': 0.10},
    'asml': {'price': 1775.64, 'prev': 1747.28, 'chg': 28.36,   'chgPct': 1.62},
    'asmi': {'price': 889.60,  'prev': 889.80,  'chg': -0.20,   'chgPct': -0.02},
    'hanmi':{'price': 207500,  'prev': 199200,  'chg': 8300,    'chgPct': 4.17},
    'psk':  {'price': 141000,  'prev': 143500,  'chg': -2500,   'chgPct': -1.74},
    'entg': {'price': 140.63,  'prev': 135.08,  'chg': 5.55,    'chgPct': 4.11},
    'soul': {'price': 304500,  'prev': 290000,  'chg': 14500,   'chgPct': 5.00},
    'tck':  {'price': 236500,  'prev': 238500,  'chg': -2000,   'chgPct': -0.84},
    'anji': {'price': 293.50,  'prev': 316.09,  'chg': -22.59,  'chgPct': -7.15},
    'tfme': {'price': 77.87,   'prev': 65.61,   'chg': 12.26,   'chgPct': 18.69},
    'snps': {'price': 425.90,  'prev': 436.63,  'chg': -10.73,  'chgPct': -2.46},
    'rmbs': {'price': 105.38,  'prev': 105.93,  'chg': -0.55,   'chgPct': -0.52},
    'ter':  {'price': 353.23,  'prev': 343.11,  'chg': 10.12,   'chgPct': 2.95},
    'adv':  {'price': 29775,   'prev': 29160,   'chg': 615,     'chgPct': 2.11},
    'tfe':  {'price': 36200,   'prev': 34450,   'chg': 1750,    'chgPct': 5.08},
    'sol':  {'price': 2085,    'prev': 2075,    'chg': 10,      'chgPct': 0.48},
}

with open('/opt/data/hermes/hbf_dashboard/index.html', 'r') as f:
    html = f.read()

for stock_id, vals in new_data.items():
    # Pattern to match: id:'STOCKID',...price:OLD,...prev:OLD,...chg:OLD,...chgPct:OLD,...
    # We replace price, prev, chg, chgPct values
    p = vals['price']
    pr = vals['prev']
    c = vals['chg']
    cp = vals['chgPct']

    # Format numbers cleanly
    def fmt(v):
        if isinstance(v, float):
            s = f"{v:.2f}"
            # Remove trailing zeros but keep at least 1 decimal if it had one
            if '.' in s:
                s = s.rstrip('0').rstrip('.')
            return s
        return str(v)

    pattern = rf"(id:'{stock_id}',.*?price:)[\d.]+(.*?prev:)[\d.-]+(.*?chg:)[\d.-]+(.*?chgPct:)[\d.-]+"
    
    def replacer(m):
        return f"{m.group(1)}{fmt(p)}{m.group(2)}{fmt(pr)}{m.group(3)}{fmt(c)}{m.group(4)}{fmt(cp)}"
    
    html = re.sub(pattern, replacer, html)

with open('/opt/data/hermes/hbf_dashboard/index.html', 'w') as f:
    f.write(html)

print("HTML updated successfully.")

# Verify
with open('/opt/data/hermes/hbf_dashboard/index.html', 'r') as f:
    updated = f.read()

# Print updated stock lines for verification
for stock_id in new_data:
    match = re.search(rf"id:'{stock_id}',.*?price:([\d.]+).*?prev:([\d.-]+).*?chg:([\d.-]+).*?chgPct:([\d.-]+)", updated)
    if match:
        print(f"{stock_id}: price={match.group(1)}, prev={match.group(2)}, chg={match.group(3)}, chgPct={match.group(4)}")
    else:
        print(f"{stock_id}: NOT FOUND")
