import resend
from datetime import datetime, timezone
from typing import List
from app.core.config import settings
from app.core.database import get_supabase
import logging

logger = logging.getLogger(__name__)

resend.api_key = settings.resend_api_key


def _send(to: List[str], subject: str, html: str) -> bool:
    try:
        resend.Emails.send({
            "from": settings.resend_from_email,
            "to": to,
            "subject": subject,
            "html": html,
        })
        return True
    except Exception as e:
        logger.error(f"Resend error: {e}")
        return False


def _log_notification(user_id: str, notif_type: str, status: str) -> None:
    db = get_supabase()
    db.table("notifications_log").insert({
        "user_id": user_id,
        "type": notif_type,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "channel": "email",
        "status": status,
    }).execute()


def send_reminder(user_id: str, email: str, full_name: str, form_title: str, closes_at: str) -> bool:
    subject = f"Formulario pendiente: {form_title}"
    html = f"""
    <p>Hola {full_name},</p>
    <p>Tienes el formulario <strong>{form_title}</strong> pendiente.</p>
    <p>Vence: <strong>{closes_at}</strong></p>
    <p>Por favor complétalo a tiempo.</p>
    """
    ok = _send([email], subject, html)
    _log_notification(user_id, "reminder", "sent" if ok else "failed")
    return ok


def send_edit_alert_to_admins(user_name: str, form_title: str) -> bool:
    if not settings.admin_email_list:
        return False
    subject = f"Edición de respuesta: {form_title}"
    html = f"""
    <p><strong>{user_name}</strong> editó su respuesta al formulario <strong>{form_title}</strong>.</p>
    <p>Revisa el panel de administración para ver los cambios.</p>
    """
    return _send(settings.admin_email_list, subject, html)


def send_deadline_warning(user_id: str, email: str, full_name: str, form_title: str, closes_at: datetime) -> bool:
    closes_str = closes_at.strftime("%d/%m/%Y %H:%M")
    subject = f"Aviso: el formulario '{form_title}' vence pronto"
    html = f"""
    <p>Hola {full_name},</p>
    <p>El formulario <strong>{form_title}</strong> vence mañana: <strong>{closes_str}</strong>.</p>
    <p>Si aún no lo has completado, hazlo antes de que cierre.</p>
    """
    ok = _send([email], subject, html)
    _log_notification(user_id, "deadline", "sent" if ok else "failed")
    return ok


def was_notified_today(user_id: str, notif_type: str) -> bool:
    db = get_supabase()
    today = datetime.now(timezone.utc).date().isoformat()
    result = (
        db.table("notifications_log")
        .select("id")
        .eq("user_id", user_id)
        .eq("type", notif_type)
        .eq("status", "sent")
        .gte("sent_at", f"{today}T00:00:00Z")
        .execute()
    )
    return bool(result.data)
