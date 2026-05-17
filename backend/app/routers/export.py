from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional

from app.middleware.auth_middleware import require_admin
from app.services.export_service import (
    export_responses_csv,
    export_responses_xlsx,
    export_summary_xlsx,
    export_incomplete_csv,
)
from app.schemas.export import ExportFormat

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/responses")
async def export_responses(
    form_id: UUID = Query(...),
    format: ExportFormat = Query(ExportFormat.csv),
    admin: dict = Depends(require_admin),
):
    if format == ExportFormat.xlsx:
        return export_responses_xlsx(str(form_id))
    return export_responses_csv(str(form_id))


@router.get("/summary")
async def export_summary(
    format: ExportFormat = Query(ExportFormat.xlsx),
    admin: dict = Depends(require_admin),
):
    return export_summary_xlsx()


@router.get("/incomplete")
async def export_incomplete(
    format: ExportFormat = Query(ExportFormat.csv),
    admin: dict = Depends(require_admin),
):
    return export_incomplete_csv()
