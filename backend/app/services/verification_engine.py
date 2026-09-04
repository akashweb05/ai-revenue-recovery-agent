from sqlalchemy.orm import Session

from app.models.action_execution import (
    ActionExecution
)

from app.models.payment_verification import (
    PaymentVerification
)

from app.models.recovery import Recovery


class VerificationEngine:

    def verify(
        self,
        db: Session,
        execution_id: int,
        payment_success: bool
    ) -> PaymentVerification:

        execution = db.get(
            ActionExecution,
            execution_id
        )

        if not execution:

            raise ValueError(
                "Execution record not found"
            )

        existing_verification = (
            db.query(PaymentVerification)
            .filter(
                PaymentVerification.execution_id
                == execution_id
            )
            .first()
        )

        if existing_verification:

            return existing_verification

        recovery = db.get(
            Recovery,
            execution.recovery_id
        )

        if not recovery:

            raise ValueError(
                "Recovery record not found"
            )

        if payment_success:

            verification_status = "success"

            verification_message = (
                "Payment successfully recovered"
            )

            recovery.status = "recovered"

        else:

            verification_status = "failed"

            verification_message = (
                "Payment was not recovered"
            )

            recovery.status = "verification_failed"

        verification = PaymentVerification(

            execution_id=execution.id,

            recovery_id=recovery.id,

            payment_verified=payment_success,

            verification_status=
                verification_status,

            verification_message=
                verification_message
        )

        db.add(verification)

        db.commit()

        db.refresh(verification)

        return verification