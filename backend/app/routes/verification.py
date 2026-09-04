from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.schemas.verification import (
    VerificationCreate
)

from app.services.verification_engine import (
    VerificationEngine
)


router = APIRouter(
    prefix="/api/verification",
    tags=["Payment Verification"]
)


@router.post("/{execution_id}")
def verify_payment(
    execution_id: int,
    data: VerificationCreate,
    db: Session = Depends(get_db)
):

    engine = VerificationEngine()

    try:

        verification = engine.verify(
            db=db,
            execution_id=execution_id,
            payment_success=data.payment_success
        )

        return {
            "id": verification.id,

            "execution_id":
                verification.execution_id,

            "recovery_id":
                verification.recovery_id,

            "payment_verified":
                verification.payment_verified,

            "verification_status":
                verification.verification_status,

            "verification_message":
                verification.verification_message
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )