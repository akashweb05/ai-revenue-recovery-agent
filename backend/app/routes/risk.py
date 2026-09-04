from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.services.revenue_monitor import RevenueMonitor


router = APIRouter(
    prefix="/api/risk",
    tags=["Revenue Risk"]
)


@router.post("/scan")
def scan_revenue_risk(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):
    monitor = RevenueMonitor()

    cases = monitor.scan_failed_payments(
        db=db,
        merchant_id=merchant_id
    )

    return {
        "created_cases": len(cases),
        "cases": [
            {
                "id": case.id,
                "payment_id": case.payment_id,
                "amount_at_risk": str(
                    case.amount_at_risk
                ),
                "risk_score": float(
                    case.risk_score
                ),
                "risk_level": case.risk_level,
                "status": case.status
            }
            for case in cases
        ]
    }