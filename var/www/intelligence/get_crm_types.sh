#!/bin/bash

# Ottieni token
TOKEN=$(curl -s -X POST "https://api.crmincloud.it/api/v1/Auth/Login" \
  -H "WebApiKey: r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu" \
  -H "Content-Type: application/json" \
  -d '{"grant_type":"password","username":"intellivoice@enduser-digital.com","password":"B4b4in4_07"}' | \
  jq -r '.access_token')

echo "Token: $TOKEN"

# Scarica tipologie
curl -X GET "https://api.crmincloud.it/api/v1/ActivityTypes" \
  -H "WebApiKey: r5l50i5lvd.YjuIXg0PPJnqzeldzCBlEpMlwqJPRPFgJppSkPu" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
