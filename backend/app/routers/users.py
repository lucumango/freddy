import csv
import io
import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List
from uuid import UUID

from app.core.database import get_supabase
from app.middleware.auth_middleware import require_admin
from app.schemas.user import UserOut, UserDetail, UserIncomplete, ImportReport
from app.services.report_service import get_incomplete_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserDetail])
async def list_users(admin: dict = Depends(require_admin)):
    db = get_supabase()
    users = db.table("users").select("*").order("full_name").execute().data
    forms = db.table("forms").select("id").eq("is_active", True).execute().data
    active_form_ids = {f["id"] for f in forms}

    result = []
    for user in users:
        subs = db.table("submissions").select("form_id").eq("user_id", user["id"]).execute().data
        submitted_form_ids = {s["form_id"] for s in subs}
        pending = [fid for fid in active_form_ids if fid not in submitted_form_ids]
        result.append({**user, "submission_count": len(subs), "pending_forms": pending})
    return result


@router.get("/incomplete", response_model=List[UserIncomplete])
async def incomplete_users(admin: dict = Depends(require_admin)):
    return get_incomplete_users()


@router.get("/{user_id}", response_model=UserDetail)
async def get_user(user_id: UUID, admin: dict = Depends(require_admin)):
    db = get_supabase()
    user = db.table("users").select("*").eq("id", str(user_id)).single().execute().data
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    subs = db.table("submissions").select("form_id").eq("user_id", str(user_id)).execute().data
    return {**user, "submission_count": len(subs), "pending_forms": []}


@router.post("/import", response_model=ImportReport)
async def import_users(
    file: UploadFile = File(...),
    dry_run: bool = Query(False),
    admin: dict = Depends(require_admin),
):
    db = get_supabase()
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    # Group rows by DNI (one user may have multiple email rows)
    user_map: dict = {}
    for row in reader:
        dni = (row.get("dni") or "").strip()
        full_name = (row.get("full_name") or "").strip()
        email = (row.get("email") or "").strip()
        if not dni:
            continue
        if dni not in user_map:
            user_map[dni] = {"full_name": full_name, "emails": []}
        if email and email not in user_map[dni]["emails"]:
            user_map[dni]["emails"].append(email)

    imported = 0
    skipped = 0
    conflicts = []

    existing_users = db.table("users").select("dni, full_name").execute().data
    existing_map = {u["dni"]: u for u in existing_users}

    for dni, data in user_map.items():
        if not re.match(r"^\d{8}$", dni):
            conflicts.append({"dni": dni, "reason": "Invalid DNI (not 8 digits)"})
            skipped += 1
            continue

        if dni in existing_map:
            existing_name = existing_map[dni].get("full_name", "")
            if existing_name and existing_name.lower() != data["full_name"].lower():
                conflicts.append({
                    "dni": dni,
                    "reason": f"Name mismatch: existing='{existing_name}', new='{data['full_name']}'",
                })
            skipped += 1
            continue

        if not dry_run:
            primary = data["emails"][0] if data["emails"] else None
            db.table("users").insert({
                "dni": dni,
                "full_name": data["full_name"],
                "emails": data["emails"],
                "primary_email": primary,
                "role": "participant",
            }).execute()

        imported += 1

    return ImportReport(imported=imported, skipped=skipped, conflicts=conflicts, dry_run=dry_run)
