#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE:-http://localhost:8000}"

echo "Waiting for API at $BASE ..."
for i in {1..30}; do
  if curl -fsS "$BASE/api/health" >/dev/null 2>&1; then
    echo "API is up ✅"
    break
  fi
  sleep 1
done

echo "Health"
curl -s "$BASE/api/health"; echo

echo "Ingest telemetry"
curl -s -X POST "$BASE/api/telemetry/ingest" \
  -H "Content-Type: application/json" \
  -d '[
    {"vin":"VIN-DEMO-001","ts":"2026-01-24T12:05:00Z","soc":18.0,"soh":92.0,"pack_voltage":310.1,"pack_current":95.0,"max_temp":52.0,"min_temp":33.0,"odo_km":1201.2},
    {"vin":"VIN-DEMO-001","ts":"2026-01-24T12:10:00Z","soc":35.5,"soh":92.0,"pack_voltage":315.0,"pack_current":70.0,"max_temp":32.0,"min_temp":24.0,"odo_km":1201.8}
  ]'; echo

echo "Latest"
curl -s "$BASE/api/telemetry/latest?vin=VIN-DEMO-001"; echo

echo "Summary"
curl -s -G "$BASE/api/telemetry/summary" \
  --data-urlencode "vin=VIN-DEMO-001" \
  --data-urlencode "from_ts=2026-01-24T11:59:00Z" \
  --data-urlencode "to_ts=2026-01-24T12:10:00Z"; echo

echo "OK ✅"
