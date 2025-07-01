#!/bin/bash
api_key=$(grep -E '^API_KEY=' .env.prod | sed 's/^API_KEY=//; s/"//g')

if [ -z "$api_key" ]; then
  echo "API_KEY not found in .env.prod"
  exit 1
fi

cids=(
  "2026416.CO"
  "2026416.CO"
  "2026417.CO"
  "2026417.CO"
  "2026418.CO"
  "2026418.CO"
  "2026419.CO"
  "2026419.CO"
  "2026420.CO"
  "2026420.CO"
  "2028097.CO"
  "2028097.CO"
  "2028769.CO"
  "2028769.CO"
  "2028772.CO"
  "2028773.CO"
  "2028772.CO"
  "2017878.CO"
  "2017883.CO"
  "2017862.CO"
  "2017863.CO"
  "2017868.CO"
  "2017864.CO"
  "2011544.CO"
  "570035.1.CO"
  "2011530.CO"
  "2018414.CO"
  "2018415.CO"
  "2013750.CO"
  "2013753.CO"
  "2013755.CO"
  "2024531.CO"
  "2024532.CO"
  "2024533.CO"
  "2017888.CO"
  "2017887.CO"
  "2011533.CO"
  "2011534.CO"
  "2011535.CO"
  "2011536.CO"
  "2011539.CO"
  "2029180.CO"
  "2029182.CO"
  "2029183.CO"
  "2038436.CO"
  "2038436.CO"
  "2039193.CO"
  "2039193.CO"
  "2039647.CO"
  "2039647.CO"
  "2039648.CO"
  "2039649.CO"
  "2043558.CO"
  "2043559.CO"
  "2043558.CO"
  "2043560.CO"
  "2043562.CO"
  "2043562.CO"
  "2043563.CO"
  "2043563.CO"
  "2043564.CO"
  "2046408.CO"
  "2046409.CO"
  "2046408.CO"
  "2046410.CO"
  "2043442.CO"
  "2043442.CO"
  "2043443.CO"
  "2043444.CO"
  "599031.1.CO"
  "2032430.CO"
  "2032430.CO"
  "2022890.CO"
  "2022891.CO"
  "2028777.TR"
  "2028779.TR"
  "495975.1.4.CO"
  "2032433.CO"
  "529081.1.2.CO"
  "2026416.CO"
  "2026417.CO"
  "2026417.CO"
  "2026418.CO"
  "2026418.CO"
  "2026419.CO"
  "2026419.CO"
  "2026420.CO"
  "2026420.CO"
  "2028097.CO"
  "2028097.CO"
  "2028769.CO"
  "2028769.CO"
  "2028772.CO"
  "2028773.CO"
  "2028772.CO"
)


# API endpoint
url="http://172.18.93.253:8051/api/tickets/create"


# Loop through each circuit id
for cid in "${cids[@]}"; do
  echo "Processing $cid..."
  curl -X 'POST' "$url" \
    -H 'accept: application/json' \
    -H "csc_token: $api_key" \
    -H 'Content-Type: application/json' \
    -d "{
    \"related_cids\": [\"$cid\"],
    \"custom_description\": \"true\",
    \"description\": \"Este es un tk de prueba, por favor hacer caso omiso, (Ver la nota del tk para ver los pasos a seguir)\",
    \"summary\": \"PASO PASO\",
    \"worklog\": \"Pr favor documentar, hacer cambios de estado y cierre correspondientes.\"
    }"
  echo -e "\n"  # Add a newline for readability between requests
done




