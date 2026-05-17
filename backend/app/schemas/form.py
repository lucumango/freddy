from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.schemas.question import QuestionCreate, QuestionOut


class FormCreate(BaseModel):
    title: str
    description: Optional[str] = None
    opens_at: Optional[datetime] = None
    closes_at: Optional[datetime] = None
    questions: List[QuestionCreate] = []


class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    opens_at: Optional[datetime] = None
    closes_at: Optional[datetime] = None


class FormOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    is_active: bool
    opens_at: Optional[datetime]
    closes_at: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class FormDetail(FormOut):
    questions: List[QuestionOut]


class FormStatus(BaseModel):
    form_id: UUID
    total_users: int
    submitted: int
    pending: int
    submitted_users: List[dict]
    pending_users: List[dict]
