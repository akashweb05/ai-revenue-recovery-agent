from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.dashboard_service import (
    DashboardService
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/metrics")
def get_dashboard_metrics(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):

    service = DashboardService()

    metrics = service.get_metrics(
        db=db,
        merchant_id=merchant_id
    )

    return metrics


@router.get("/summary")
def get_dashboard_summary(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):

    service = DashboardService()

    summary = service.get_summary(
        db=db,
        merchant_id=merchant_id
    )

    return summary


@router.get("/cases")
def get_dashboard_cases(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):

    service = DashboardService()

    return service.get_cases(
        db=db,
        merchant_id=merchant_id
    )


@router.get("/cases/{risk_case_id}")
def get_dashboard_case(
    risk_case_id: int,
    db: Session = Depends(get_db)
):

    service = DashboardService()

    case = service.get_case(
        db=db,
        risk_case_id=risk_case_id
    )

    if case is None:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found"
        )

    return case


@router.get("/cases/{risk_case_id}/timeline")
def get_dashboard_case_timeline(
    risk_case_id: int,
    db: Session = Depends(get_db)
):

    service = DashboardService()

    timeline = service.get_case_timeline(
        db=db,
        risk_case_id=risk_case_id
    )

    if timeline is None:
        raise HTTPException(
            status_code=404,
            detail="Recovery case not found"
        )

    return timeline