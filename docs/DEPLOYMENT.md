# Deployment Guide

## Supabase Setup

1. Go to https://supabase.com and create a project (or use existing: `yiwzdybujjvqsuslnkzy`)
2. In the SQL Editor, run `supabase/migrations/001_initial_schema.sql`
3. Collect these values from Project Settings > API:
   - `SUPABASE_URL`
   - `SUPABASE_PUBLISHABLE_KEY` (anon key)
   - `SUPABASE_SERVICE_ROLE_KEY` (secret — never expose in frontend)
   - `SUPABASE_JWT_SECRET` (from Settings > API > JWT Settings)

## Resend Setup

1. Create account at https://resend.com (free: 3000 emails/month)
2. Add and verify your domain (or use `onboarding@resend.dev` for testing)
3. Create an API key → set as `RESEND_API_KEY`
4. Set `RESEND_FROM_EMAIL` to your verified sender address
5. Set `RESEND_ADMIN_EMAILS` to comma-separated admin emails

## Local Development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with real values
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs
```

## Render Deployment

1. Create a new **Web Service** on https://render.com
2. Connect your GitHub repo
3. Set:
   - **Root directory**: `backend`
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add all environment variables from `.env.example` in the Render dashboard
5. Deploy

## Environment Variables Reference

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key (admin) |
| `SUPABASE_JWT_SECRET` | JWT signing secret |
| `RESEND_API_KEY` | Resend API key |
| `RESEND_FROM_EMAIL` | Verified sender email |
| `RESEND_ADMIN_EMAILS` | Comma-separated admin emails |

## Creating the First Admin

After deploying, create an admin user directly in Supabase:

```sql
-- 1. Create the auth user via Supabase dashboard (Auth > Users > Add user)
-- 2. Then in SQL Editor:
INSERT INTO users (id, dni, full_name, emails, primary_email, role)
VALUES (
  '<auth-user-uuid>',
  '12345678',
  'Admin Name',
  ARRAY['admin@example.com'],
  'admin@example.com',
  'admin'
);
```
