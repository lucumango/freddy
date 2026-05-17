# QHub Course Management Platform

Backend API for managing forms, responses, and ~60 participants for QuantumHub Peru.

## Stack

- **Python 3.12** + **FastAPI** + **Pydantic v2**
- **Supabase** (PostgreSQL + Auth)
- **Resend** (email notifications, free tier: 3000/month)
- **openpyxl** + csv (Excel/CSV export)
- **APScheduler** (auto open/close forms, deadline warnings)

## Quick Start

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
uvicorn app.main:app --reload
# Open http://localhost:8000/docs
```

## Environment Variables

See `backend/.env.example` for all required variables.

## Database

Run `supabase/migrations/001_initial_schema.sql` in your Supabase SQL editor.

## Project Structure

```
backend/
  app/
    main.py              # FastAPI app + scheduler
    core/                # config, database, security
    routers/             # auth, forms, questions, responses, users, export, reports
    models/              # enums and dataclasses
    schemas/             # Pydantic request/response schemas
    services/            # notification, export, report logic
    middleware/          # JWT auth + role checking
  tests/                 # pytest test suite
data/
  participants.csv        # participant list (from repo)
  form_responses.csv      # sample form responses (from repo)
supabase/
  migrations/
    001_initial_schema.sql
docs/
  API.md                 # endpoint reference
  DATABASE.md            # schema docs
  DEPLOYMENT.md          # Render + Supabase setup
  NOTIFICATIONS.md       # Resend setup
  EXPORT_GUIDE.md        # pandas examples
  ADMIN_GUIDE.md         # admin operations
  USER_STORIES.md        # full user stories
```

## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Key Features

- DNI-based authentication (via Supabase Auth email bridge)
- One submission per user per form, editable while form is active
- Admin email alerts on submission edits
- Scheduled form open/close + daily deadline warnings
- CSV/Excel export with dynamic columns per form
- Bulk user import from CSV with conflict detection
- Data quality reports (missing DNI, name, email)
