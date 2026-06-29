import json
import re

# Load fetched prices
with open('/opt/data/hermes/hbf_dashboard/prices.json') as f:
    prices = json.load(f)

# Read current HTML
with open('/opt/data/hermes/hbf_dashboard/index.html', 'r') as f:
    html = f.read()

def fmt_num(v):
    """Format number for JS - avoid floating point artifacts."""
    if v is None:
        return "null"
    if v == int(v):
        return str(int(v))
    # Round to 2 decimal places for chg values
    return f"{v:.2f}"

# Compute updates
updates = {}
for stock_id, data in prices.items():
    price = data['price']
    prev = data['prev'] if data['prev'] else price
    chg = price - prev
    chgPct = round(chg / prev * 100, 2) if prev != 0 else 0
    updates[stock_id] = {
        'price': fmt_num(price),
        'prev': fmt_num(prev),
        'chg': fmt_num(chg),
        'chgPct': str(chgPct)
    }

def update_stock_line(match):
    stock_id = match.group(1)
    if stock_id not in updates or stock_id == 'kioxia':
        return match.group(0)
    u = updates[stock_id]
    line = match.group(0)
    
    # Replace price:
    line = re.sub(r'price:([\d.]+|null)', f"price:{u['price']}", line)
    # Replace prev:
    line = re.sub(r'prev:([\d.]+|null)', f"prev:{u['prev']}", line)
    # Replace chg: (signed number or null)
    line = re.sub(r'chg:(-?[\d.]+|null)', f"chg:{u['chg']}", line)
    # Replace chgPct:
    line = re.sub(r'chgPct:(-?[\d.]+|null)', f"chgPct:{u['chgPct']}", line)
    
    return line

pattern = r"\{id:'(\w+)',name:'[^']*',ticker:'[^']*'[^}]*(?:\{[^}]*\})?\}"

html = re.sub(pattern, update_stock_line, html)

with open('/opt/data/hermes/hbf_dashboard/index.html', 'w') as f:
    f.write(html)

print("HTML updated (clean)!")
for stock_id, u in updates.items():
    print(f"{stock_id}: price={u['price']}, prev={u['prev']}, chg={u['chg']}, chgPct={u['chgPct']}%")
