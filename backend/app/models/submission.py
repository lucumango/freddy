from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass
class SubmissionInfo:
    id: UUID
    form_id: UUID
    user_id: UUID
    submitted_at: datetime
    last_edited_at: Optional[datetime]
    edit_count: int
    admin_notified_of_edit: bool
