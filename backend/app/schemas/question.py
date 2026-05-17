from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from app.models.question import QuestionType


class QuestionCreate(BaseModel):
    label: str
    type: QuestionType
    order_index: int = 0
    required: bool = True
    options: Optional[Dict[str, Any]] = None


class QuestionUpdate(BaseModel):
    label: Optional[str] = None
    type: Optional[QuestionType] = None
    order_index: Optional[int] = None
    required: Optional[bool] = None
    options: Optional[Dict[str, Any]] = None


class QuestionOut(BaseModel):
    id: UUID
    form_id: UUID
    order_index: int
    label: str
    type: QuestionType
    required: bool
    options: Optional[Dict[str, Any]]
    created_at: datetime


class ReorderRequest(BaseModel):
    question_ids: List[UUID]
