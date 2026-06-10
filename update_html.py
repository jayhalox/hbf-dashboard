import json

# Load fetched prices
with open('/opt/data/hermes/hbf_dashboard/prices.json') as f:
    prices = json.load(f)

# Compute chg from closes (last close = price, second-to-last = prev)
for sid, data in prices.items():
    closes = data.get('closes', [])
    if len(closes) >= 2:
        price = closes[-1]
        prev = closes[-2]
        chg = round(price - prev, 2)
        chgPct = round((price - prev) / prev * 100, 2) if prev != 0 else 0
    elif len(closes) == 1:
        price = closes[0]
        prev = closes[0]
        chg = 0
        chgPct = 0
    else:
        price = None
        prev = None
        chg = None
        chgPct = None
    data['price'] = price
    data['prev'] = prev
    data['chg'] = chg
    data['chgPct'] = chgPct

# Print summary
for sid, data in prices.items():
    print(f"{sid}: price={data['price']}, prev={data['prev']}, chg={data['chg']}, chgPct={data['chgPct']}%")

# Save updated prices
with open('/opt/data/hermes/hbf_dashboard/prices.json', 'w') as f:
    json.dump(prices, f, indent=2)

# Read index.html
with open('/opt/data/hermes/hbf_dashboard/index.html', 'r') as f:
    html = f.read()

# Each stock line contains: id:'SID', ... price:XXX,prev:XXX,chg:XXX,chgPct:XXX,
# We'll find by id pattern and replace the four fields
for sid in prices:
    data = prices[sid]
    if data['price'] is None:
        print(f"SKIP {sid}: no price data")
        continue

    price = data['price']
    prev = data['prev']
    chg = data['chg']
    chgPct = data['chgPct']

    # Format values
    is_int_stock = sid in ('sk', 'ss', 'hanmi', 'psk', 'soul', 'tck', 'tel', 'adv', 'tfe')
    if is_int_stock:
        price_str = str(int(price))
        prev_str = str(int(prev))
        chg_str = str(int(chg))
        chgPct_str = f"{chgPct:.2f}"
    else:
        price_str = f"{price:.2f}"
        prev_str = f"{prev:.2f}"
        chg_str = f"{chg:.2f}"
        chgPct_str = f"{chgPct:.2f}"

    # Find the position of this stock's entry
    marker = "id:'" + sid + "',"
    idx = html.find(marker)
    if idx == -1:
        print(f"NOT FOUND: {sid}")
        continue

    # Find the price field after this marker
    # The fields we need to replace are: price:OLD, prev:OLD, chg:OLD, chgPct:OLD
    section = html[idx:idx+500]  # Look within 500 chars

    # Find and replace price
    price_marker = "price:"
    p_idx = section.find(price_marker)
    p_start = p_idx + len(price_marker)
    p_end = section.find(",", p_start)
    old_price = section[p_start:p_end]

    # Find prev
    prev_marker = "prev:"
    pv_idx = section.find(prev_marker)
    pv_start = pv_idx + len(prev_marker)
    pv_end = section.find(",", pv_start)
    old_prev = section[pv_start:pv_end]

    # Find chg (but not chgPct)
    chg_marker = "chg:"
    c_idx = section.find(chg_marker)
    c_start = c_idx + len(chg_marker)
    c_end = section.find(",", c_start)
    old_chg = section[c_start:c_end]

    # Find chgPct
    chgpct_marker = "chgPct:"
    cp_idx = section.find(chgpct_marker)
    cp_start = cp_idx + len(chgpct_marker)
    # chgPct might be followed by , or }
    cp_end_comma = section.find(",", cp_start)
    cp_end_brace = section.find("}", cp_start)
    cp_end = min(cp_end_comma if cp_end_comma > 0 else 999, cp_end_brace if cp_end_brace > 0 else 999)
    old_chgPct = section[cp_start:cp_end]

    # Now replace in the full html
    html = html[:idx + p_start] + price_str + html[idx + p_end:]
    # Re-find after price replacement
    section = html[idx:idx+500]
    pv_idx = section.find(prev_marker)
    pv_start = pv_idx + len(prev_marker)
    pv_end = section.find(",", pv_start)
    html = html[:idx + pv_start] + prev_str + html[idx + pv_end:]

    section = html[idx:idx+500]
    c_idx = section.find(chg_marker)
    c_start = c_idx + len(chg_marker)
    c_end = section.find(",", c_start)
    html = html[:idx + c_start] + chg_str + html[idx + c_end:]

    section = html[idx:idx+500]
    cp_idx = section.find(chgpct_marker)
    cp_start = cp_idx + len(chgpct_marker)
    cp_end_comma = section.find(",", cp_start)
    cp_end_brace = section.find("}", cp_start)
    cp_end = min(cp_end_comma if cp_end_comma > 0 else 999, cp_end_brace if cp_end_brace > 0 else 999)
    html = html[:idx + cp_start] + chgPct_str + html[idx + cp_end:]

    print(f"  OK {sid}: {old_price}→{price_str}, {old_prev}→{prev_str}, {old_chg}→{chg_str}, {old_chgPct}→{chgPct_str}")

# Write updated HTML
with open('/opt/data/hermes/hbf_dashboard/index.html', 'w') as f:
    f.write(html)

print("\n=== HTML UPDATED ===")
