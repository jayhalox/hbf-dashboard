#!/usr/bin/env python3
"""Generate the new STOCKS array from prices.json"""
import json, random
random.seed(42)

with open('/opt/data/hermes/hbf_dashboard/prices.json') as f:
    prices = json.load(f)

stock_defs = {
    'sk': ('SK hynix', '000660.KS', 'KR', 'idm'),
    'ss': ('Samsung', '005930.KS', 'KR', 'idm'),
    'wdc': ('SanDisk / WD', 'WDC', 'US', 'idm'),
    'mu': ('Micron', 'MU', 'US', 'idm'),
    'amat': ('Applied Materials', 'AMAT', 'US', 'equip'),
    'tel': ('Tokyo Electron', '8035.T', 'JP', 'equip'),
    'asml': ('ASML', 'ASML', 'NL', 'equip'),
    'asmi': ('ASM International', 'ASM.AS', 'NL', 'equip'),
    'hanmi': ('HMI Semiconductor', '042700.KS', 'KR', 'equip'),
    'psk': ('PSK Holdings', '031980.KS', 'KR', 'equip'),
    'entg': ('Entegris', 'ENTG', 'US', 'equip'),
    'soul': ('Soulbrain', '357780.KS', 'KR', 'equip'),
    'tck': ('TCK', '064760.KS', 'KR', 'equip'),
    'anji': ('Anji Micro', '688019.SS', 'CN', 'equip'),
    'tfme': ('TFME (Tongfu)', '002156.SZ', 'CN', 'equip'),
    'snps': ('Synopsys', 'SNPS', 'US', 'test'),
    'rmbs': ('Rambus', 'RMBS', 'US', 'test'),
    'ter': ('Teradyne', 'TER', 'US', 'test'),
    'adv': ('Advantest', '6857.T', 'JP', 'test'),
    'tfe': ('TFE', '425420.KS', 'KR', 'test'),
    'sol': ('SOL AI Semiconductor ETF', '473050.KS', 'KR', 'test'),
}

# Read the HTML to get the Korean names and emoji flags
with open('/opt/data/hermes/hbf_dashboard/index.html') as f:
    html = f.read()

import re
# Extract existing stock entries to preserve names, flags, and notes
pattern = r"\{id:'(\w+)',name:'([^']*)',ticker:'([^']*)',country:'([^']*)',flag:'([^']*)',step:'([^']*)',(.*?)\},"
matches = re.findall(pattern, html)
existing = {}
for m in matches:
    sid = m[0]
    existing[sid] = {
        'name': m[1],
        'ticker': m[2],
        'country': m[3],
        'flag': m[4],
        'step': m[5],
        'rest': m[6]
    }

extras_notes = {
    'wdc': ",note:'⚠️ HBF 최초 고안·OCP 표준화 주도'",
    'snps': ",note:'🔑 HBF 인터페이스 IP 주도'",
    'rmbs': ",note:'🔑 HBF 컨트롤러 IP'",
}

def gen_spark(up):
    vals = []
    v = random.randint(0, 30) if up else random.randint(70, 100)
    for _ in range(13):
        delta = random.randint(-12, 12)
        if up:
            v = min(100, max(0, v + delta + 2))
        else:
            v = min(100, max(0, v + delta - 2))
        vals.append(v)
    if up:
        vals[0] = random.randint(0, 25)
        vals[-1] = random.randint(80, 100)
    else:
        vals[0] = random.randint(75, 100)
        vals[-1] = random.randint(0, 25)
    return vals

order = ['sk','ss','wdc','mu','amat','tel','asml','asmi','hanmi','psk','entg','soul','tck','anji','tfme','snps','rmbs','ter','adv','tfe','sol']

lines = []
for sid in order:
    p = prices[sid]
    ex = existing.get(sid, {})
    name = ex.get('name', sid)
    flag = ex.get('flag', '')
    country = ex.get('country', '')
    step = ex.get('step', '')
    ticker = ex.get('ticker', '')
    up = p['chg'] > 0
    spark = gen_spark(up)
    note = extras_notes.get(sid, '')
    
    def fmt_num(v):
        if v is None: return 'null'
        if isinstance(v, float) and v == int(v): return str(int(v))
        return str(v)
    
    line = f"  {{id:'{sid}',name:'{name}',ticker:'{ticker}',country:'{country}',flag:'{flag}',step:'{step}',price:{fmt_num(p['price'])},prev:{fmt_num(p['prev'])},chg:{fmt_num(p['chg'])},chgPct:{p['chgPct']},spark:{spark}{note}}},"
    lines.append(line)

# Insert kioxia after mu
kioxia = "  {id:'kioxia',name:'Kioxia',ticker:'(비상장)',country:'JP',flag:'🇯🇵',step:'idm',price:null,prev:null,chg:null,chgPct:null,spark:null,note:'샌디스크와 낸드 합작'},"
lines.insert(4, kioxia)

print('\n'.join(lines))
