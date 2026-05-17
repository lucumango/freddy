# API Reference

Full interactive docs at `http://localhost:8000/docs` (Swagger UI).

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | None | DNI + password → JWT (rate limited 10/min) |
| POST | `/auth/register` | Admin | Register a participant |
| POST | `/auth/link-email` | Participant | Add email to account |
| POST | `/auth/link-phone` | Participant | Add phone number |
| POST | `/auth/change-password` | Participant | Change own password |

## Forms

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/forms` | Any | List forms (participants see active only) |
| POST | `/forms` | Admin | Create form with questions |
| GET | `/forms/{id}` | Any | Form detail with questions |
| PUT | `/forms/{id}` | Admin | Update form metadata |
| DELETE | `/forms/{id}` | Admin | Soft-close form |
| PATCH | `/forms/{id}/toggle` | Admin | Open/close form |
| GET | `/forms/{id}/status` | Admin | Submission status (who's pending) |

## Questions (nested under forms)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/forms/{id}/questions` | Admin | Add question |
| PUT | `/forms/{id}/questions/{qid}` | Admin | Edit question |
| DELETE | `/forms/{id}/questions/{qid}` | Admin | Remove question |
| PATCH | `/forms/{id}/questions/reorder` | Admin | Reorder by id list |

## Responses

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/responses/submit` | Participant | Submit form (409 if already submitted) |
| PUT | `/responses/{submission_id}` | Participant | Edit submission (alerts admins) |
| GET | `/responses/my` | Participant | List own submissions |
| GET | `/responses/{submission_id}` | Participant | View own answers |

## Users

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users` | Admin | List all users with stats |
| GET | `/users/incomplete` | Admin | Users with data quality issues |
| GET | `/users/{id}` | Admin | User detail |
| POST | `/users/import` | Admin | Bulk CSV import (`?dry_run=true` for preview) |

## Export

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/export/responses` | Admin | `?form_id=X&format=csv\|xlsx` |
| GET | `/export/summary` | Admin | `?format=xlsx` — users x forms pivot |
| GET | `/export/incomplete` | Admin | `?format=csv` — data quality report |

## Reports

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/reports/completion` | Admin | `?form_id=X` — completion stats |
| GET | `/reports/incomplete-users` | Admin | Data quality issues |
| POST | `/reports/notify-pending` | Admin | `?form_id=X` — send reminder emails |

## Common Response Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | Deleted |
| 400 | Bad request (form closed, etc.) |
| 401 | Missing or invalid JWT |
| 403 | Insufficient role |
| 404 | Not found |
| 409 | Conflict (duplicate submission, duplicate DNI) |
| 422 | Validation error |
| 429 | Rate limit exceeded |
