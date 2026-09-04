from sqlalchemy.orm import Session

from app.models.recovery import Recovery
from app.models.policy_evaluation import (
    PolicyEvaluation
)


class PolicyEngine:

    MAX_RETRIES = 3
    MAX_REMINDERS = 2
    MAX_PAYMENT_LINKS = 2

    def evaluate(
        self,
        db: Session,
        recovery_id: int
    ) -> PolicyEvaluation:

        recovery = db.get(
            Recovery,
            recovery_id
        )

        if not recovery:

            raise ValueError(
                "Recovery record not found"
            )

        requested_action = (
            recovery.recommended_intervention
        )

        previous_attempts = (
            db.query(PolicyEvaluation)
            .filter(
                PolicyEvaluation.recovery_id
                == recovery_id,

                PolicyEvaluation.requested_action
                == requested_action,

                PolicyEvaluation.is_allowed
                == True
            )
            .count()
        )

        allowed = True
        reason = ""
        escalation_required = False

        if requested_action == "retry":

            if previous_attempts >= self.MAX_RETRIES:

                allowed = False

                reason = (
                    "Maximum retry limit reached"
                )

                escalation_required = True

            else:

                reason = (
                    "Retry allowed within policy limit"
                )

        elif requested_action == "reminder":

            if previous_attempts >= self.MAX_REMINDERS:

                allowed = False

                reason = (
                    "Maximum reminder limit reached"
                )

                escalation_required = True

            else:

                reason = (
                    "Reminder allowed within policy limit"
                )

        elif requested_action == "payment_link":

            if (
                previous_attempts
                >= self.MAX_PAYMENT_LINKS
            ):

                allowed = False

                reason = (
                    "Maximum payment link limit reached"
                )

                escalation_required = True

            else:

                reason = (
                    "Payment link allowed within policy limit"
                )

        else:

            allowed = False

            reason = (
                "Unknown recovery action"
            )

            escalation_required = True

        evaluation = PolicyEvaluation(

            recovery_id=recovery.id,

            requested_action=requested_action,

            is_allowed=allowed,

            reason=reason,

            attempt_count=previous_attempts + 1,

            escalation_required=
                escalation_required
        )

        db.add(evaluation)

        db.commit()

        db.refresh(evaluation)

        return evaluation