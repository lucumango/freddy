from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FormStatus:
    is_active: bool
    opens_at: Optional[datetime]
    closes_at: Optional[datetime]
