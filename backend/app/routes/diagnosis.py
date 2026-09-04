from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.diagnosis_engine import (
    DiagnosisEngine
)


router = APIRouter(
    prefix="/api/diagnosis",
    tags=["AI Diagnosis"]
)


@router.post("/{risk_case_id}")
def diagnose_risk_case(
    risk_case_id: int,
    db: Session = Depends(get_db)
):

    engine = DiagnosisEngine()

    try:

        diagnosis = engine.diagnose(
            db=db,
            risk_case_id=risk_case_id
        )

        return {
            "id": diagnosis.id,
            "risk_case_id":
                diagnosis.risk_case_id,

            "diagnosis_type":
                diagnosis.diagnosis_type,

            "root_cause":
                diagnosis.root_cause,

            "explanation":
                diagnosis.explanation,

            "confidence_score":
                float(
                    diagnosis.confidence_score
                ),

            "recommended_action":
                diagnosis.recommended_action
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )