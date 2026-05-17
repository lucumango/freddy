from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_supabase
from app.middleware.auth_middleware import require_admin
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionOut, ReorderRequest

router = APIRouter(prefix="/forms/{form_id}/questions", tags=["questions"])


def _assert_form(db, form_id: str):
    form = db.table("forms").select("id").eq("id", form_id).single().execute().data
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")


@router.post("", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
async def add_question(form_id: UUID, body: QuestionCreate, admin: dict = Depends(require_admin)):
    db = get_supabase()
    _assert_form(db, str(form_id))
    row = db.table("questions").insert({
        "form_id": str(form_id),
        "order_index": body.order_index,
        "label": body.label,
        "type": body.type,
        "required": body.required,
        "options": body.options,
    }).execute().data[0]
    return row


@router.put("/{question_id}", response_model=QuestionOut)
async def update_question(form_id: UUID, question_id: UUID, body: QuestionUpdate, admin: dict = Depends(require_admin)):
    db = get_supabase()
    updates = body.model_dump(exclude_none=True)
    result = (
        db.table("questions")
        .update(updates)
        .eq("id", str(question_id))
        .eq("form_id", str(form_id))
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")
    return result.data[0]


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(form_id: UUID, question_id: UUID, admin: dict = Depends(require_admin)):
    db = get_supabase()
    db.table("questions").delete().eq("id", str(question_id)).eq("form_id", str(form_id)).execute()


@router.patch("/reorder")
async def reorder_questions(form_id: UUID, body: ReorderRequest, admin: dict = Depends(require_admin)):
    db = get_supabase()
    for idx, qid in enumerate(body.question_ids):
        db.table("questions").update({"order_index": idx}).eq("id", str(qid)).eq("form_id", str(form_id)).execute()
    return {"reordered": len(body.question_ids)}
