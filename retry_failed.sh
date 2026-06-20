#!/bin/bash
# Retry failed stocks with longer delays
RAWDIR="/opt/data/hermes/hbf_dashboard/raw_responses"

# Retry these 14 failed stocks
TICKERS=(
  "sk:000660.KS" "ss:005930.KS" "wdc:WDC" "tel:8035.T"
  "asml:ASML" "entg:ENTG" "soul:357780.KS" "anji:688019.SS"
  "snps:SNPS" "rmbs:RMBS" "ter:TER" "adv:6857.T"
  "tfe:425420.KS" "sol:473050.KS"
)

declare -A UAS
UAS[0]="Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"
UAS[1]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
UAS[2]="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
UAS[3]="Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

for entry in "${TICKERS[@]}"; do
  key="${entry%%:*}"
  ticker="${entry##*:}"
  
  ua_idx=$((RANDOM % 4))
  UA="${UAS[$ua_idx]}"
  
  echo -n "Retrying $key ($ticker)... " >&2
  
  HTTP_CODE=$(curl -s -o "${RAWDIR}/${key}.json" -w "%{http_code}" --max-time 15 \
    "https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d" \
    -H "User-Agent: ${UA}" \
    -H "Accept: application/json" \
    -H "Accept-Language: en-US,en;q=0.9" 2>/dev/null)
  
  echo "HTTP $HTTP_CODE" >&2
  
  # 6-9 second delay between requests
  sleep $((6 + RANDOM % 4))
done

echo "Retry complete" >&2