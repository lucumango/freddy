from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class AnswerIn(BaseModel):
    question_id: UUID
    value: str


class SubmitFormRequest(BaseModel):
    form_id: UUID
    answers: List[AnswerIn]


class EditSubmissionRequest(BaseModel):
    answers: List[AnswerIn]


class AnswerOut(BaseModel):
    question_id: UUID
    question_label: str
    value: str
    updated_at: datetime


class SubmissionOut(BaseModel):
    id: UUID
    form_id: UUID
    form_title: str
    user_id: UUID
    submitted_at: datetime
    last_edited_at: Optional[datetime]
    edit_count: int
    answers: List[AnswerOut] = []
