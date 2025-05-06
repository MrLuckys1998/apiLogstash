#!/bin/bash
echo "Insertando documentos de prueba en logs-api..."

# 1. avg_threshold
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "latency": 120
}'

# 2. count_threshold
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "message": "count threshold test"
}'

# 3. (missing_data) -> No se ingesta nada a propósito

# 4. field_value_missing
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "status_code": 404
}'

# 5. ratio_between_fields
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "errors": 20,
  "requests": 50
}'

# 6. unique_terms_missing
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "service": "servicioX"
}'

# 7. multi_field_values
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "status": 500,
  "error": "Timeout"
}'

# 8. sum_threshold
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "duration": 10000
}'

# 9. min_threshold
curl -u admin:temporal -s -X POST https://wtslcccelkp0050.unix.wtes.corp:9200/watcher-pruebas/_doc -H 'Content-Type: application/json' -d '{
  "@timestamp": "'$(date -Iseconds)'",
  "temperature": 2
}'

echo "Documentos insertados."
