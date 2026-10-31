from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import AdminServiceDep, require_admin
from app.dto.accounts import AccountResponse
from app.dto.reports import (
    BulkDeleteRequest,
    BulkDeleteResponse,
    ReportListResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/reports")
def list_reports(admin: AdminServiceDep) -> ReportListResponse:
    return admin.reports()


@router.post("/reports/{report_id}/hide", status_code=status.HTTP_204_NO_CONTENT)
def hide_report(report_id: int, admin: AdminServiceDep) -> Response:
    admin.hide_report(report_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/items/bulk-delete")
def bulk_delete(body: BulkDeleteRequest, admin: AdminServiceDep) -> BulkDeleteResponse:
    return admin.bulk_delete(body)


@router.put("/accounts/{username}/admin")
def make_admin(username: str, admin: AdminServiceDep) -> AccountResponse:
    return admin.make_admin(username)


@router.delete("/accounts/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(username: str, admin: AdminServiceDep) -> Response:
    admin.anonymize_account(username)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
