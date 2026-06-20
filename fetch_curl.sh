#!/bin/bash
# Fetch stock prices one at a time using curl with random delays
OUTFILE="/opt/data/hermes/hbf_dashboard/current_prices.json"
TICKERS=(
  "sk:000660.KS" "ss:005930.KS" "wdc:WDC" "mu:MU" "amat:AMAT" "tel:8035.T"
  "asml:ASML" "asmi:ASM" "hanmi:042700.KS" "psk:031980.KS" "entg:ENTG"
  "soul:357780.KS" "tck:064760.KS" "anji:688019.SS" "tfme:002156.SZ"
  "snps:SNPS" "rmbs:RMBS" "ter:TER" "adv:6857.T" "tfe:425420.KS" "sol:473050.KS"
)

echo "{"
first=true
for entry in "${TICKERS[@]}"; do
  key="${entry%%:*}"
  ticker="${entry##*:}"
  sleep $((2 + RANDOM % 3))  # 2-4 second delay
  
  # Rotate User-Agents
  case $((RANDOM % 4)) in
    0) UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" ;;
    1) UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15" ;;
    2) UA="Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0" ;;
    3) UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1" ;;
  esac
  
  RAW=$(curl -s --max-time 15 \
    "https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d" \
    -H "User-Agent: ${UA}" 2>/dev/null)
  
  if [ -z "$RAW" ] || echo "$RAW" | grep -q "Too Many Requests"; then
    echo "  \"${key}\": {\"price\": null, \"prev\": null, \"error\": \"rate_limited\"}"
  else
    # Parse with python
    python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
m = data['chart']['result'][0]['meta']
price = m.get('regularMarketPrice')
prev = m.get('chartPreviousClose') or m.get('previousClose')
print(json.dumps({'price': price, 'prev': prev}))
" <<< "$RAW" 2>/dev/null || echo "  \"${key}\": {\"price\": null, \"prev\": null, \"error\": \"parse_error\"}"
  fi
  
  [ "$first" = false ] && echo ","
  first=false
done
echo "}"