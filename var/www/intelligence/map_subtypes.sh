#!/bin/bash

# Lista degli ID da mappare
IDS=(64030 63705 63689 63688 63565 61887 61886 61633 61632 61631 61630 61629 61628 61627 61626 61625 61492 61491 61490 61489)

# Token (riusa quello di prima)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VySWQiOiIxMjYzNzAiLCJDdXN0b21lcklkIjoiNDA1NTEiLCJuYmYiOjE3NTM4MTkxMTcsImV4cCI6MTc1MzgyMDMxNywiaWF0IjoxNzUzODE5MTE3fQ.8kLiyTO7sCREhJDAuaJVJdlwvhw1dhwNIF7jKae0PVU"

echo "Mapping SubType ID → Nome:"
echo "========================="

for id in "${IDS[@]}"; do
    echo -n "$id: "
    
    # Chiamata API con rate limiting
    sleep 1.5
    
    response=$(curl -s -X GET "https://api.crmincloud.it/api/v1/ActivitySubType/$id" \
        -H "WebApiKey: r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu" \
        -H "Authorization: Bearer $TOKEN")
    
    # Estrai il nome dal JSON
    name=$(echo "$response" | jq -r '.name // .description // "ERRORE"')
    
    echo "$name"
done
