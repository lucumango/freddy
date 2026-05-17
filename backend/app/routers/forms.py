from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_supabase
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.form import FormCreate, FormUpdate, FormOut, FormDetail, FormStatus
from app.schemas.question import QuestionOut

router = APIRouter(prefix="/forms", tags=["forms"])


@router.get("", response_model=List[FormOut])
async def list_forms(current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    if current_user["role"] == "admin":
        result = db.table("forms").select("*").order("created_at", desc=True).execute()
    else:
        now = datetime.now(timezone.utc).isoformat()
        result = (
            db.table("forms")
            .select("*")
            .eq("is_active", True)
            .or_(f"closes_at.is.null,closes_at.gt.{now}")
            .order("created_at", desc=True)
            .execute()
        )
    return result.data


@router.post("", response_model=FormDetail, status_code=status.HTTP_201_CREATED)
async def create_form(body: FormCreate, admin: dict = Depends(require_admin)):
    db = get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    form_row = db.table("forms").insert({
        "title": body.title,
        "description": body.description,
        "opens_at": body.opens_at.isoformat() if body.opens_at else None,
        "closes_at": body.closes_at.isoformat() if body.closes_at else None,
        "is_active": False,
        "created_by": admin["id"],
        "created_at": now,
        "updated_at": now,
    }).execute().data[0]

    questions_out = []
    for i, q in enumerate(body.questions):
        q_row = db.table("questions").insert({
            "form_id": form_row["id"],
            "order_index": q.order_index or i,
            "label": q.label,
            "type": q.type,
            "required": q.required,
            "options": q.options,
        }).execute().data[0]
        questions_out.append(q_row)

    return {**form_row, "questions": questions_out}


@router.get("/{form_id}", response_model=FormDetail)
async def get_form(form_id: UUID, current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    form = db.table("forms").select("*").eq("id", str(form_id)).single().execute().data
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    questions = db.table("questions").select("*").eq("form_id", str(form_id)).order("order_index").execute().data
    return {**form, "questions": questions}


@router.put("/{form_id}", response_model=FormOut)
async def update_form(form_id: UUID, body: FormUpdate, admin: dict = Depends(require_admin)):
    db = get_supabase()
    updates = body.model_dump(exclude_none=True)
    if "opens_at" in updates and updates["opens_at"]:
        updates["opens_at"] = updates["opens_at"].isoformat()
    if "closes_at" in updates and updates["closes_at"]:
        updates["closes_at"] = updates["closes_at"].isoformat()
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = db.table("forms").update(updates).eq("id", str(form_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Form not found")
    return result.data[0]


@router.delete("/{form_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_form(form_id: UUID, admin: dict = Depends(require_admin)):
    db = get_supabase()
    db.table("forms").update({"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", str(form_id)).execute()


@router.patch("/{form_id}/toggle")
async def toggle_form(form_id: UUID, admin: dict = Depends(require_admin)):
    db = get_supabase()
    form = db.table("forms").select("is_active").eq("id", str(form_id)).single().execute().data
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    new_state = not form["is_active"]
    db.table("forms").update({"is_active": new_state, "updated_at": datetime.now(timezone.utc).isoformat()}).eq("id", str(form_id)).execute()
    return {"is_active": new_state}


@router.get("/{form_id}/status", response_model=FormStatus)
async def form_status(form_id: UUID, admin: dict = Depends(require_admin)):
    db = get_supabase()
    users = db.table("users").select("id, dni, full_name, primary_email, emails").eq("role", "participant").execute().data
    submissions = db.table("submissions").select("user_id, submitted_at").eq("form_id", str(form_id)).execute().data
    submitted_ids = {s["user_id"] for s in submissions}

    submitted = []
    pending = []
    for u in users:
        email = u.get("primary_email") or (u.get("emails") or [""])[0]
        info = {"id": u["id"], "dni": u.get("dni"), "full_name": u.get("full_name"), "email": email}
        (submitted if u["id"] in submitted_ids else pending).append(info)

    return {
        "form_id": str(form_id),
        "total_users": len(users),
        "submitted": len(submitted),
        "pending": len(pending),
        "submitted_users": submitted,
        "pending_users": pending,
    }
