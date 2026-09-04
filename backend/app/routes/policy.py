from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.policy_engine import (
    PolicyEngine
)


router = APIRouter(
    prefix="/api/policy",
    tags=["Policy Engine"]
)


@router.post("/{recovery_id}")
def evaluate_policy(
    recovery_id: int,
    db: Session = Depends(get_db)
):

    engine = PolicyEngine()

    try:

        evaluation = engine.evaluate(
            db=db,
            recovery_id=recovery_id
        )

        return {
            "id": evaluation.id,

            "recovery_id":
                evaluation.recovery_id,

            "requested_action":
                evaluation.requested_action,

            "is_allowed":
                evaluation.is_allowed,

            "reason":
                evaluation.reason,

            "attempt_count":
                evaluation.attempt_count,

            "escalation_required":
                evaluation.escalation_required
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )