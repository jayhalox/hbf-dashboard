#!/bin/bash
# Fetch each stock's raw JSON response to a separate file, then parse all
RAWDIR="/opt/data/hermes/hbf_dashboard/raw_responses"
mkdir -p "$RAWDIR"

TICKERS=(
  "sk:000660.KS" "ss:005930.KS" "wdc:WDC" "mu:MU" "amat:AMAT" "tel:8035.T"
  "asml:ASML" "asmi:ASM" "hanmi:042700.KS" "psk:031980.KS" "entg:ENTG"
  "soul:357780.KS" "tck:064760.KS" "anji:688019.SS" "tfme:002156.SZ"
  "snps:SNPS" "rmbs:RMBS" "ter:TER" "adv:6857.T" "tfe:425420.KS" "sol:473050.KS"
)

declare -A UAS
UAS[0]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
UAS[1]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
UAS[2]="Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"
UAS[3]="Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"

for entry in "${TICKERS[@]}"; do
  key="${entry%%:*}"
  ticker="${entry##*:}"
  
  # Rotate User-Agent
  ua_idx=$((RANDOM % 4))
  UA="${UAS[$ua_idx]}"
  
  echo -n "Fetching $key ($ticker)... " >&2
  
  HTTP_CODE=$(curl -s -o "${RAWDIR}/${key}.json" -w "%{http_code}" --max-time 15 \
    "https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d" \
    -H "User-Agent: ${UA}" 2>/dev/null)
  
  echo "HTTP $HTTP_CODE" >&2
  
  # Random delay between 2-5 seconds to avoid rate limits
  sleep $((2 + RANDOM % 4))
done

echo "All raw responses saved to $RAWDIR" >&2