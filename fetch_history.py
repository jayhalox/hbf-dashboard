#!/usr/bin/env python3
"""Fetch 6-month historical data for 21 HBF stocks. Sample to max 60 points each."""
import json
import urllib.request
import time
import sys
import random

STOCKS = {
    'sk': '000660.KS', 'ss': '005930.KS', 'wdc': 'WDC', 'mu': 'MU',
    'amat': 'AMAT', 'tel': '8035.T', 'asml': 'ASML', 'asmi': 'ASM',
    'hanmi': '042700.KS', 'psk': '031980.KS', 'entg': 'ENTG',
    'soul': '357780.KS', 'tck': '064760.KS', 'anji': '688019.SS',
    'tfme': '002156.SZ', 'snps': 'SNPS', 'rmbs': 'RMBS', 'ter': 'TER',
    'adv': '6857.T', 'tfe': '425420.KS', 'sol': '473050.KS'
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

MAX_POINTS = 60

def fetch_history(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=6mo"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data['chart']['result'][0]
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        opens = quotes['open']
        highs = quotes['high']
        lows = quotes['low']
        closes = quotes['close']
        volumes = quotes['volume']
        
        points = []
        for i in range(len(timestamps)):
            if closes[i] is not None:
                points.append({
                    't': timestamps[i],
                    'o': opens[i] if opens[i] is not None else closes[i],
                    'h': highs[i] if highs[i] is not None else closes[i],
                    'l': lows[i] if lows[i] is not None else closes[i],
                    'c': closes[i],
                    'v': volumes[i] if volumes[i] is not None else 0
                })
        
        # Sample to max_points
        if len(points) > MAX_POINTS:
            step = len(points) / MAX_POINTS
            sampled = []
            for j in range(MAX_POINTS):
                idx = min(int(j * step), len(points) - 1)
                sampled.append(points[idx])
            # Ensure first and last
            if sampled[0]['t'] != points[0]['t']:
                sampled[0] = points[0]
            if sampled[-1]['t'] != points[-1]['t']:
                sampled[-1] = points[-1]
            points = sampled
        
        return points
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return None

results = {}
for sid, ticker in STOCKS.items():
    print(f"Fetching history for {sid} ({ticker})...", file=sys.stderr)
    data = fetch_history(ticker)
    if data:
        # Only keep required fields for data.json: t, c, h, l, v
        results[sid] = [{'t': p['t'], 'c': p['c'], 'h': p['h'], 'l': p['l'], 'v': p['v']} for p in data]
        print(f"  -> {len(results[sid])} points, first: {data[0]['c']}, last: {data[-1]['c']}", file=sys.stderr)
    else:
        print(f"  -> FAILED", file=sys.stderr)
        results[sid] = []
    # Random delay to avoid rate limiting
    time.sleep(0.3 + random.random() * 0.4)

with open('/opt/data/hermes/hbf_dashboard/data.json', 'w') as f:
    json.dump(results, f)

print(f"\nSaved data.json with {len(results)} stocks", file=sys.stderr)
