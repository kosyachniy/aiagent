#!/usr/bin/env bash
#chmod +x scripts/set_business_priority.sh

# Usage: ./scripts/set_business_priority.sh "Your CEO speech text here"

API_URL="http://localhost:8000/admin/business-priority"
# If your admin endpoint requires a Bearer token, set it here or export ADMIN_TOKEN
ADMIN_TOKEN=""

if [ -z "$1" ]; then
  echo "Usage: $0 'Your CEO speech text'"
  exit 1
fi

# Escape any quotes in the speech text
speech=$(printf '%s' "$1" | sed 's/"/\\"/g')
payload="{\"speech\":\"$speech\"}"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  $( [ -n "$ADMIN_TOKEN" ] && printf '-H "Authorization: Bearer %s" ' "$ADMIN_TOKEN" ) \
  -d "$payload"

echo
