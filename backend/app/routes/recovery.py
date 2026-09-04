from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.recovery_engine import (
    RecoveryEngine
)

from app.services.recovery_orchestrator import (
    RecoveryOrchestrator
)

router = APIRouter(
    prefix="/api/recovery",
    tags=["Recovery Agent"]
)

@router.post("/process")
def process_failed_payments(
    merchant_id: int | None = None,
    db: Session = Depends(get_db)
):

    orchestrator = RecoveryOrchestrator()

    try:

        result = orchestrator.process(
            db=db,
            merchant_id=merchant_id
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.post("/{risk_case_id}")
def analyze_recovery(
    risk_case_id: int,
    db: Session = Depends(get_db)
):

    engine = RecoveryEngine()

    try:

        recovery = engine.analyze(
            db=db,
            risk_case_id=risk_case_id
        )

        return {
            "id": recovery.id,
            "risk_case_id":
                recovery.risk_case_id,

            "diagnosis_id":
                recovery.diagnosis_id,

            "recovery_probability":
                float(
                    recovery.recovery_probability
                ),

            "recommended_intervention":
                recovery.recommended_intervention,

            "status":
                recovery.status
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )