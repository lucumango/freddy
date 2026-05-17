from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_supabase
from app.middleware.auth_middleware import get_current_user
from app.schemas.response import SubmitFormRequest, EditSubmissionRequest, SubmissionOut
from app.services.notification_service import send_edit_alert_to_admins

router = APIRouter(prefix="/responses", tags=["responses"])


@router.post("/submit", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_form(body: SubmitFormRequest, current_user: dict = Depends(get_current_user)):
    db = get_supabase()

    existing = (
        db.table("submissions")
        .select("id")
        .eq("form_id", str(body.form_id))
        .eq("user_id", current_user["id"])
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already submitted. Use PUT to edit.")

    form = db.table("forms").select("title, is_active").eq("id", str(body.form_id)).single().execute().data
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    if not form["is_active"]:
        raise HTTPException(status_code=400, detail="Form is not active")

    now = datetime.now(timezone.utc).isoformat()
    submission = db.table("submissions").insert({
        "form_id": str(body.form_id),
        "user_id": current_user["id"],
        "submitted_at": now,
        "edit_count": 0,
        "admin_notified_of_edit": False,
    }).execute().data[0]

    for ans in body.answers:
        db.table("responses").insert({
            "submission_id": submission["id"],
            "question_id": str(ans.question_id),
            "value": ans.value,
            "created_at": now,
            "updated_at": now,
        }).execute()

    return _build_submission_out(db, submission, form["title"])


@router.put("/{submission_id}", response_model=SubmissionOut)
async def edit_submission(submission_id: UUID, body: EditSubmissionRequest, current_user: dict = Depends(get_current_user)):
    db = get_supabase()

    submission = (
        db.table("submissions")
        .select("*")
        .eq("id", str(submission_id))
        .eq("user_id", current_user["id"])
        .single()
        .execute()
        .data
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    form = db.table("forms").select("title, is_active").eq("id", submission["form_id"]).single().execute().data
    if not form or not form["is_active"]:
        raise HTTPException(status_code=400, detail="Form is closed")

    now = datetime.now(timezone.utc).isoformat()
    db.table("submissions").update({
        "last_edited_at": now,
        "edit_count": submission["edit_count"] + 1,
        "admin_notified_of_edit": False,
    }).eq("id", str(submission_id)).execute()

    for ans in body.answers:
        existing_ans = (
            db.table("responses")
            .select("id")
            .eq("submission_id", str(submission_id))
            .eq("question_id", str(ans.question_id))
            .execute()
            .data
        )
        if existing_ans:
            db.table("responses").update({"value": ans.value, "updated_at": now}).eq("id", existing_ans[0]["id"]).execute()
        else:
            db.table("responses").insert({
                "submission_id": str(submission_id),
                "question_id": str(ans.question_id),
                "value": ans.value,
                "created_at": now,
                "updated_at": now,
            }).execute()

    send_edit_alert_to_admins(current_user.get("full_name", "Unknown"), form["title"])

    updated = db.table("submissions").select("*").eq("id", str(submission_id)).single().execute().data
    return _build_submission_out(db, updated, form["title"])


@router.get("/my", response_model=List[SubmissionOut])
async def my_submissions(current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    submissions = db.table("submissions").select("*").eq("user_id", current_user["id"]).execute().data
    result = []
    for sub in submissions:
        form = db.table("forms").select("title").eq("id", sub["form_id"]).single().execute().data
        result.append(_build_submission_out(db, sub, form["title"] if form else ""))
    return result


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(submission_id: UUID, current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    submission = (
        db.table("submissions")
        .select("*")
        .eq("id", str(submission_id))
        .eq("user_id", current_user["id"])
        .single()
        .execute()
        .data
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    form = db.table("forms").select("title").eq("id", submission["form_id"]).single().execute().data
    return _build_submission_out(db, submission, form["title"] if form else "")


def _build_submission_out(db, submission: dict, form_title: str) -> dict:
    answers_raw = (
        db.table("responses")
        .select("question_id, value, updated_at")
        .eq("submission_id", submission["id"])
        .execute()
        .data
    )
    answers = []
    for a in answers_raw:
        q = db.table("questions").select("label").eq("id", a["question_id"]).single().execute().data
        answers.append({
            "question_id": a["question_id"],
            "question_label": q["label"] if q else "",
            "value": a["value"],
            "updated_at": a["updated_at"],
        })
    return {
        "id": submission["id"],
        "form_id": submission["form_id"],
        "form_title": form_title,
        "user_id": submission["user_id"],
        "submitted_at": submission["submitted_at"],
        "last_edited_at": submission.get("last_edited_at"),
        "edit_count": submission["edit_count"],
        "answers": answers,
    }
