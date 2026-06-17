#!/usr/bin/env python3
"""Generate the new STOCKS array for index.html"""
import json
import random
random.seed(42)

prices_raw = {
    "sk": {"price":2382000,"prev":2048000,"chg":334000,"chgPct":16.31},
    "ss": {"price":343000,"prev":302500,"chg":40500,"chgPct":13.39},
    "wdc": {"price":681.08,"prev":517.72,"chg":163.36,"chgPct":31.55},
    "mu": {"price":1020.76,"prev":935.89,"chg":84.87,"chgPct":9.07},
    "amat": {"price":568.23,"prev":499.21,"chg":69.02,"chgPct":13.83},
    "tel": {"price":70860,"prev":63400,"chg":7460,"chgPct":11.77},
    "asml": {"price":1803.89,"prev":1777.77,"chg":26.12,"chgPct":1.47},
    "asmi": {"price":6.95,"prev":5.77,"chg":1.18,"chgPct":20.45},
    "hanmi": {"price":328500,"prev":270000,"chg":58500,"chgPct":21.67},
    "psk": {"price":64000,"prev":138700,"chg":-74700,"chgPct":-53.86},
    "entg": {"price":151.61,"prev":134.35,"chg":17.26,"chgPct":12.85},
    "soul": {"price":281000,"prev":338500,"chg":-57500,"chgPct":-16.99},
    "tck": {"price":119900,"prev":253500,"chg":-133600,"chgPct":-52.70},
    "anji": {"price":232.88,"prev":216.40,"chg":16.48,"chgPct":7.62},
    "tfme": {"price":62.93,"prev":61.44,"chg":1.49,"chgPct":2.43},
    "snps": {"price":448.38,"prev":465.27,"chg":-16.89,"chgPct":-3.63},
    "rmbs": {"price":132.48,"prev":146.84,"chg":-14.36,"chgPct":-9.78},
    "ter": {"price":409.35,"prev":369.21,"chg":40.14,"chgPct":10.87},
    "adv": {"price":30340,"prev":25175,"chg":5165,"chgPct":20.52},
    "tfe": {"price":26250,"prev":50800,"chg":-24550,"chgPct":-48.33},
    "sol": {"price":2055,"prev":2075,"chg":-20,"chgPct":-0.96},
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
    # force trend
    if up:
        vals[0] = random.randint(0, 25)
        vals[-1] = random.randint(80, 100)
    else:
        vals[0] = random.randint(75, 100)
        vals[-1] = random.randint(0, 25)
    return vals

stock_defs = {
    "sk": ('SK hynix', '000660.KS', 'KR', '🇰🇷', 'idm'),
    "ss": ('Samsung', '005930.KS', 'KR', '🇰🇷', 'idm'),
    "wdc": ('SanDisk / WD', 'WDC', 'US', '🇺🇸', 'idm'),
    "mu": ('Micron', 'MU', 'US', '🇺🇸', 'idm'),
    "amat": ('Applied Materials', 'AMAT', 'US', '🇺🇸', 'equip'),
    "tel": ('Tokyo Electron', '8035.T', 'JP', '🇯🇵', 'equip'),
    "asml": ('ASML', 'ASML', 'NL', '🇳🇱', 'equip'),
    "asmi": ('ASM International', 'ASM', 'NL', '🇳🇱', 'equip'),
    "hanmi": ('한미반도체', '042700.KS', 'KR', '🇰🇷', 'equip'),
    "psk": ('PSK Holdings', '031980.KS', 'KR', '🇰🇷', 'equip'),
    "entg": ('Entegris', 'ENTG', 'US', '🇺🇸', 'equip'),
    "soul": ('솔브레인', '357780.KS', 'KR', '🇰🇷', 'equip'),
    "tck": ('티씨케이', '064760.KS', 'KR', '🇰🇷', 'equip'),
    "anji": ('Anji Micro', '688019.SS', 'CN', '🇨🇳', 'equip'),
    "tfme": ('TFME (通富)', '002156.SZ', 'CN', '🇨🇳', 'equip'),
    "snps": ('Synopsys', 'SNPS', 'US', '🇺🇸', 'test'),
    "rmbs": ('Rambus', 'RMBS', 'US', '🇺🇸', 'test'),
    "ter": ('Teradyne', 'TER', 'US', '🇺🇸', 'test'),
    "adv": ('Advantest', '6857.T', 'JP', '🇯🇵', 'test'),
    "tfe": ('티에프이', '425420.KS', 'KR', '🇰🇷', 'test'),
    "sol": ('SOL AI소부장 ETF', '473050.KS', 'KR', '🇰🇷', 'test'),
}

lines = []
for sid, p in prices_raw.items():
    name, ticker, country, flag, step = stock_defs[sid]
    up = p["chg"] > 0
    spark = gen_spark(up)
    
    extras = ""
    if sid == "wdc":
        extras = ",note:'⚠️ HBF 최초 고안·OCP 표준화 주도'"
    elif sid == "snps":
        extras = ",note:'🔑 HBF 인터페이스 IP 주도'"
    elif sid == "rmbs":
        extras = ",note:'🔑 HBF 컨트롤러 IP'"
    
    line = f"  {{id:'{sid}',name:'{name}',ticker:'{ticker}',country:'{country}',flag:'{flag}',step:'{step}',price:{p['price']},prev:{p['prev']},chg:{p['chg']},chgPct:{p['chgPct']},spark:{spark}{extras}}},"
    lines.append(line)

# insert kioxia at position 4 (after mu, before amat)
kioxia = "  {id:'kioxia',name:'Kioxia',ticker:'(비상장)',country:'JP',flag:'🇯🇵',step:'idm',price:null,prev:null,chg:null,chgPct:null,spark:null,note:'샌디스크와 낸드 합작'},"
lines.insert(4, kioxia)

print("\n".join(lines))
