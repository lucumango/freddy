# Admin Guide

## Getting Started

1. Log in with your admin DNI and password: `POST /auth/login`
2. Copy the `access_token` from the response
3. Use it in all subsequent requests: `Authorization: Bearer <token>`

## Managing Forms

### Create a form with questions
```bash
curl -X POST http://localhost:8000/forms \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Encuesta Semanal #1",
    "description": "Retroalimentación de la primera semana",
    "closes_at": "2026-05-23T23:59:00Z",
    "questions": [
      {"label": "Nombres", "type": "short_text", "order_index": 0},
      {"label": "¿Cómo te fue esta semana?", "type": "long_text", "order_index": 1},
      {"label": "Del 1 al 5, ¿cómo calificarías el módulo?", "type": "likert", "order_index": 2,
       "options": {"min": 1, "max": 5, "min_label": "Muy difícil", "max_label": "Muy fácil"}}
    ]
  }'
```

### Open/close a form manually
```bash
curl -X PATCH http://localhost:8000/forms/FORM_UUID/toggle \
  -H "Authorization: Bearer $TOKEN"
```

### Check submission status
```bash
curl http://localhost:8000/forms/FORM_UUID/status \
  -H "Authorization: Bearer $TOKEN"
```

## Managing Users

### Import participants from CSV
CSV must have columns: `dni`, `full_name`, `email`

```bash
# Dry run first
curl -X POST "http://localhost:8000/users/import?dry_run=true" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@participants.csv"

# Commit import
curl -X POST "http://localhost:8000/users/import" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@participants.csv"
```

### Find incomplete profiles
```bash
curl http://localhost:8000/users/incomplete \
  -H "Authorization: Bearer $TOKEN"
```

## Sending Reminders

```bash
# Send reminder to all pending users for a form (respects 24h cooldown)
curl -X POST "http://localhost:8000/reports/notify-pending?form_id=FORM_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

## Exporting Data

```bash
# CSV for pandas/Excel analysis
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/responses?form_id=FORM_UUID&format=csv" \
  -o responses.csv

# Formatted Excel with color-coded completion
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/summary?format=xlsx" \
  -o summary.xlsx
```

## Completion Report

```bash
curl "http://localhost:8000/reports/completion?form_id=FORM_UUID" \
  -H "Authorization: Bearer $TOKEN"
```

Returns: `{ total_users, submitted, pending, completion_rate, submitted_users[], pending_users[] }`
