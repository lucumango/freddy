# Export Guide

## Downloading Exports

All export endpoints require an admin JWT in the `Authorization: Bearer <token>` header.

```bash
# CSV responses for a specific form
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/responses?form_id=FORM_UUID&format=csv" \
  -o responses.csv

# Excel responses
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/responses?form_id=FORM_UUID&format=xlsx" \
  -o responses.xlsx

# Completion summary (all users x all forms)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/summary?format=xlsx" \
  -o summary.xlsx

# Incomplete users report
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/export/incomplete?format=csv" \
  -o incomplete.csv
```

## CSV Column Schema

```
submission_id, submitted_at, last_edited_at, edit_count,
user_dni, user_full_name, user_email, form_title,
[question_label_1], [question_label_2], ...
```

- UTF-8 BOM included for Excel compatibility
- Dates in ISO 8601 format
- No merged cells

## Pandas Examples

```python
import pandas as pd

# Load responses
df = pd.read_csv('responses.csv', encoding='utf-8-sig')

# --- Completion rate per question ---
for col in df.columns[8:]:  # skip metadata columns
    filled = df[col].notna() & (df[col] != '')
    print(f"{col}: {filled.mean()*100:.1f}% answered")

# --- Likert scale mean per question ---
likert_cols = ['¿Qué tan motivado/a te sientes?']  # replace with actual labels
for col in likert_cols:
    numeric = pd.to_numeric(df[col], errors='coerce')
    print(f"{col}: mean={numeric.mean():.2f}, std={numeric.std():.2f}")

# --- Pivot by user ---
pivot = df.pivot_table(
    index=['user_dni', 'user_full_name'],
    columns='form_title',
    values='submitted_at',
    aggfunc='first'
)
pivot['submitted'] = pivot.notna().any(axis=1)
print(pivot)

# --- Submissions per day ---
df['date'] = pd.to_datetime(df['submitted_at']).dt.date
daily = df.groupby('date').size()
print(daily)

# --- Users who edited their submission ---
edited = df[df['edit_count'] > 0][['user_full_name', 'edit_count', 'last_edited_at']]
print(edited.sort_values('edit_count', ascending=False))

# --- Export filtered subset ---
week1 = df[pd.to_datetime(df['submitted_at']) < '2026-05-01']
week1.to_excel('week1_responses.xlsx', index=False)
```
