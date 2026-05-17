from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from enum import Enum


class ExportFormat(str, Enum):
    csv = "csv"
    xlsx = "xlsx"


class ExportParams(BaseModel):
    form_id: Optional[UUID] = None
    format: ExportFormat = ExportFormat.csv
