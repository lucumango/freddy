from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID

from app.core.database import get_supabase
from app.middleware.auth_middleware import require_admin
from app.services.report_service import get_completion_report, get_incomplete_users
from app.services.notification_service import send_reminder, was_notified_today

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/completion")
async def completion_report(form_id: UUID = Query(...), admin: dict = Depends(require_admin)):
    return get_completion_report(str(form_id))


@router.get("/incomplete-users")
async def incomplete_users_report(admin: dict = Depends(require_admin)):
    return get_incomplete_users()


@router.post("/notify-pending")
async def notify_pending(form_id: UUID = Query(...), admin: dict = Depends(require_admin)):
    db = get_supabase()
    report = get_completion_report(str(form_id))
    form = db.table("forms").select("title, closes_at").eq("id", str(form_id)).single().execute().data
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    sent = 0
    skipped = 0

    for user in report["pending_users"]:
        if was_notified_today(user["id"], "reminder"):
            skipped += 1
            continue
        email = user.get("email", "")
        if not email:
            skipped += 1
            continue
        closes_str = form.get("closes_at", "Sin fecha de cierre")
        ok = send_reminder(
            user_id=user["id"],
            email=email,
            full_name=user.get("full_name", "Participante"),
            form_title=form["title"],
            closes_at=closes_str,
        )
        sent += (1 if ok else 0)
        skipped += (0 if ok else 1)

    return {"sent": sent, "skipped_cooldown_or_no_email": skipped}
