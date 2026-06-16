import re

# Read current HTML
with open('/opt/data/hermes/hbf_dashboard/index.html', 'r') as f:
    html = f.read()

# Price data from fetch (price, prev)
prices = {
    "sk":  (2288000, 2150000), "ss":  (337000, 322500),
    "wdc": (653.53, 562.93),   "mu":  (1087.99, 981.61),
    "amat":(585.78, 567.25),   "tel": (72760, 68000),
    "asml":(1892.66, 1863.55), "asmi":(6.83, 6.39),
    "hanmi":(347000, 361000),  "psk": (135600, 152300),
    "entg":(162.89, 150.52),   "soul":(427000, 441500),
    "tck": (290500, 290000),   "anji":(233.67, 225.00),
    "tfme":(61.54, 57.22),     "snps":(454.38, 453.89),
    "rmbs":(143.29, 146.56),   "ter": (432.41, 403.20),
    "adv": (29420, 27325),     "tfe": (57100, 57300),
    "sol": (2080, 2080),
}

# Generate spark arrays (normalized 0-100, resampled to 13 points)
spark_closes = {
    "sk": [2048000, 2101000, 2150000, 2288000],
    "ss": [302500, 299000, 322500, 337000],
    "wdc": [517.72, 490.09, 529.29, 562.93, 653.53],
    "mu": [935.89, 891.88, 995.87, 981.61, 1087.99],
    "amat": [499.21, 497.01, 552.64, 567.25, 585.78],
    "tel": [61830, 63400, 68000, 72760],
    "asml": [1777.77, 1734.19, 1899.48, 1863.55, 1892.66],
    "asmi": [5.77, 5.48, 5.98, 6.39, 6.83],
    "hanmi": [270000, 291000, 361000, 347000],
    "psk": [138700, 133900, 152300, 135600],
    "entg": [134.35, 128.88, 144.92, 150.52, 162.89],
    "soul": [338500, 355000, 441500, 427000],
    "tck": [253500, 277500, 290000, 290500],
    "anji": [214.82, 216.40, 230.45, 225.00, 233.67],
    "tfme": [64.43, 61.44, 60.09, 57.22, 61.54],
    "snps": [465.27, 460.54, 456.29, 453.89, 454.38],
    "rmbs": [146.84, 138.12, 144.47, 146.56, 143.29],
    "ter": [369.21, 347.59, 381.40, 403.20, 432.41],
    "adv": [25235, 25175, 27325, 29420],
    "tfe": [50800, 57300, 57100],
    "sol": [2075, 2070, 2080, 2080],
}

def make_spark(closes):
    if not closes or len(closes) < 2:
        return None
    mn, mx = min(closes), max(closes)
    rng = mx - mn if mx != mn else 1
    normalized = [(c - mn) / rng * 100 for c in closes]
    n = 13
    result = []
    for i in range(n):
        idx = i * (len(normalized) - 1) / (n - 1)
        lo = int(idx)
        hi = min(lo + 1, len(normalized) - 1)
        frac = idx - lo
        val = normalized[lo] * (1 - frac) + normalized[hi] * frac
        result.append(round(val))
    return result

count = 0
for stock_id, (price, prev) in prices.items():
    chg = price - prev
    chg_pct = round((chg / prev) * 100, 2) if prev != 0 else 0.0
    
    # Format numbers
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.2f}"
        return str(int(v))
    
    price_str = fmt(price)
    prev_str = fmt(prev)
    chg_str = fmt(chg)
    
    # Generate spark
    spark = make_spark(spark_closes.get(stock_id, []))
    
    # Build pattern to match: price:NNN,prev:NNN,chg:NNN,chgPct:NNN,spark:[...]
    pattern = re.compile(
        r"(\{id:'" + stock_id + r"',[^}]*?price:)" + r"([^,]+)" +
        r"(,prev:)" + r"([^,]+)" +
        r"(,chg:)" + r"([^,]+)" +
        r"(,chgPct:)" + r"([^,]+)" +
        r"(,spark:)\[[^\]]*\]"
    )
    
    # Use mutable list to track count from inside lambda
    cnt = [0]
    
    def make_replacer(_price_str, _prev_str, _chg_str, _chg_pct, _spark):
        def replacer(m):
            cnt[0] += 1
            spark_str = f"[{','.join(map(str, _spark))}]" if _spark else "null"
            return (m.group(1) + _price_str + 
                    m.group(3) + _prev_str + 
                    m.group(5) + _chg_str + 
                    m.group(7) + str(_chg_pct) + 
                    m.group(9) + spark_str)
        return replacer
    
    html, n = pattern.subn(make_replacer(price_str, prev_str, chg_str, chg_pct, spark), html)
    if n == 0:
        print(f"WARNING: Could not find pattern for {stock_id}")
    else:
        count += n
        direction = "▲" if chg > 0 else "▼" if chg < 0 else "─"
        print(f"UPDATED: {stock_id}: {prev_str} → {price_str} ({direction} {chg_str}, {chg_pct:+.2f}%)")

# Write back
with open('/opt/data/hermes/hbf_dashboard/index.html', 'w') as f:
    f.write(html)

print(f"\nTotal stocks updated: {count}")
