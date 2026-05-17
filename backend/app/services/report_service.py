import re
from typing import List, Dict, Any
from app.core.database import get_supabase


def _is_valid_dni(dni: str) -> bool:
    return bool(dni and re.match(r"^\d{8}$", str(dni)))


def get_incomplete_users() -> List[Dict[str, Any]]:
    db = get_supabase()

    users = db.table("users").select("*").eq("role", "participant").execute().data
    active_forms = db.table("forms").select("id, title").eq("is_active", True).execute().data
    submissions = db.table("submissions").select("user_id, form_id").execute().data

    submitted_map: Dict[str, set] = {}
    for s in submissions:
        submitted_map.setdefault(s["user_id"], set()).add(s["form_id"])

    result = []
    for user in users:
        emails = user.get("emails") or []
        no_email = len(emails) == 0
        multiple_emails_no_primary = len(emails) > 3 and not user.get("primary_email")
        missing_name = not (user.get("full_name") or "").strip()
        missing_dni = not _is_valid_dni(user.get("dni", ""))

        user_submitted = submitted_map.get(user["id"], set())
        pending = [f["title"] for f in active_forms if f["id"] not in user_submitted]

        if missing_name or missing_dni or no_email or multiple_emails_no_primary or pending:
            result.append({
                "id": user["id"],
                "dni": user.get("dni"),
                "full_name": user.get("full_name"),
                "missing_name": missing_name,
                "missing_dni": missing_dni,
                "no_email": no_email,
                "multiple_emails_no_primary": multiple_emails_no_primary,
                "pending_forms": pending,
            })
    return result


def get_completion_report(form_id: str) -> Dict[str, Any]:
    db = get_supabase()

    users = db.table("users").select("id, dni, full_name, primary_email, emails").eq("role", "participant").execute().data
    submissions = db.table("submissions").select("user_id, submitted_at").eq("form_id", form_id).execute().data
    submitted_ids = {s["user_id"] for s in submissions}

    submitted_users = []
    pending_users = []

    for user in users:
        email = user.get("primary_email") or (user.get("emails") or [""])[0]
        info = {"id": user["id"], "dni": user.get("dni"), "full_name": user.get("full_name"), "email": email}
        if user["id"] in submitted_ids:
            submitted_users.append(info)
        else:
            pending_users.append(info)

    total = len(users)
    return {
        "form_id": form_id,
        "total_users": total,
        "submitted": len(submitted_users),
        "pending": len(pending_users),
        "completion_rate": round(len(submitted_users) / total * 100, 1) if total else 0,
        "submitted_users": submitted_users,
        "pending_users": pending_users,
    }
