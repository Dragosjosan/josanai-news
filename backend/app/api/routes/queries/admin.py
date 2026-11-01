from fastapi import APIRouter, Depends

from app.api.dependencies import AdminServiceDep, require_admin
from app.dto.reports import ReportListResponse

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/reports")
def list_reports(admin: AdminServiceDep) -> ReportListResponse:
    return admin.reports()
