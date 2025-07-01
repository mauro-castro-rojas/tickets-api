#!/bin/bash
api_key=$(grep -E '^API_KEY=' .env.dev | sed "s/^API_KEY=//; s/'//g; s/\"//g")
running_url=$(grep -E '^RUNNING_API_URL=' .env.dev | sed "s/^RUNNING_API_URL=//; s/'//g; s/\"//g")


if [ -z "$api_key" ]; then
  echo "API_KEY not found in .env.prod"
  exit 1
fi

cid="2029933.CO"

url="$running_url/api/tickets/create"

echo "Processing $cid..."
echo "URL: $url"

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
 





