import json, urllib.request

url = "https://query1.finance.yahoo.com/v8/finance/chart/WDC?interval=1d&range=5d"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    d = json.loads(resp.read())
meta = d["chart"]["result"][0]["meta"]
print(json.dumps(meta, indent=2))
