from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.models.user import UserRole


class UserOut(BaseModel):
    id: UUID
    dni: str
    full_name: Optional[str]
    emails: List[str]
    primary_email: Optional[str]
    phone: Optional[str]
    role: UserRole
    created_at: datetime


class UserDetail(UserOut):
    submission_count: int = 0
    pending_forms: List[str] = []


class UserIncomplete(BaseModel):
    id: UUID
    dni: Optional[str]
    full_name: Optional[str]
    missing_name: bool
    missing_dni: bool
    no_email: bool
    multiple_emails_no_primary: bool
    pending_forms: List[str]


class ImportRow(BaseModel):
    dni: str
    full_name: str
    email: EmailStr


class ImportReport(BaseModel):
    imported: int
    skipped: int
    conflicts: List[dict]
    dry_run: bool
