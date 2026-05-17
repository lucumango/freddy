# Notifications Guide

## Provider: Resend

Free tier: 3,000 emails/month (enough for ~60 students).

## Email Templates

### reminder
Triggered by `POST /reports/notify-pending` or the daily scheduler.

```
Subject: Formulario pendiente: {form_title}
Body:    Hola {full_name}, tienes el formulario '{form_title}' pendiente.
         Vence: {closes_at}
```

### edit_alert
Triggered automatically when a participant edits their submission.
Sent to all admin emails in `RESEND_ADMIN_EMAILS`.

```
Subject: Edición de respuesta: {form_title}
Body:    {user_name} editó su respuesta al formulario '{form_title}'.
```

### deadline_warning
Sent daily at 9am Lima time (UTC-5 = 14:00 UTC) to users who have
a pending form closing within the next 24 hours.
Respects cooldown: not resent if already sent today for the same type.

## Cooldown Logic

`was_notified_today(user_id, type)` checks `notifications_log` for
a `sent` record from midnight UTC to now. If found, the email is skipped.

## Customizing Templates

Edit `app/services/notification_service.py` — each template is an
inline HTML string in its own function:
- `send_reminder()`
- `send_edit_alert_to_admins()`
- `send_deadline_warning()`

Replace the `html` variable with your own HTML or a loaded template file.

## Scheduler

Uses APScheduler (AsyncIOScheduler) started in FastAPI lifespan:
- **Every hour**: auto-open/close forms based on `opens_at`/`closes_at`
- **Daily 14:00 UTC**: send deadline warnings for forms closing within 24h

The scheduler runs in-process. For production with multiple workers,
use a separate worker process or a Supabase Edge Function for cron.
