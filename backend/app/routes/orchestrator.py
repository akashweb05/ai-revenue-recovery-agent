from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import (
    get_db
)

from app.services.recovery_orchestrator import (
    RecoveryOrchestrator
)


router = APIRouter(
    prefix="/api/recovery",
    tags=["Recovery Orchestrator"]
)


@router.post("/process")
def process_failed_payments(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):

    orchestrator = (
        RecoveryOrchestrator()
    )

    try:

        results = (
            orchestrator.process_failed_payments(
                db=db,
                merchant_id=merchant_id
            )
        )

        return {
            "processed_cases":
                len(results),

            "results":
                results
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )