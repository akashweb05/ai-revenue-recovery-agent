from sqlalchemy.orm import Session

from app.services.revenue_monitor import (
    RevenueMonitor
)

from app.services.diagnosis_engine import (
    DiagnosisEngine
)

from app.services.recovery_engine import (
    RecoveryEngine
)

from app.services.policy_engine import (
    PolicyEngine
)

from app.services.execution_engine import (
    ExecutionEngine
)


class RecoveryOrchestrator:

    def __init__(self):

        self.revenue_monitor = (
            RevenueMonitor()
        )

        self.diagnosis_engine = (
            DiagnosisEngine()
        )

        self.recovery_engine = (
            RecoveryEngine()
        )

        self.policy_engine = (
            PolicyEngine()
        )

        self.execution_engine = (
            ExecutionEngine()
        )


    def process(
        self,
        db: Session,
        merchant_id: int | None = None
    ):

        # Step 1:
        # Find failed payments and create
        # revenue risk cases

        risk_cases = (
            self.revenue_monitor
            .scan_failed_payments(
                db=db,
                merchant_id=merchant_id
            )
        )

        results = []

        for risk_case in risk_cases:

            # Step 2:
            # Diagnose the failure

            diagnosis = (
                self.diagnosis_engine
                .diagnose(
                    db=db,
                    risk_case_id=risk_case.id
                )
            )


            # Step 3:
            # Calculate recovery probability
            # and choose intervention

            recovery = (
                self.recovery_engine
                .analyze(
                    db=db,
                    risk_case_id=risk_case.id
                )
            )


            # Step 4:
            # Check policy

            policy = (
                self.policy_engine
                .evaluate(
                    db=db,
                    recovery_id=recovery.id
                )
            )


            # Prepare base result

            result = {

                "risk_case_id":
                    risk_case.id,

                "payment_id":
                    risk_case.payment_id,

                "diagnosis_type":
                    diagnosis.diagnosis_type,

                "recovery_probability":
                    float(
                        recovery.recovery_probability
                    ),

                "recommended_action":
                    recovery.recommended_intervention,

                "policy_allowed":
                    policy.is_allowed,

                "policy_reason":
                    policy.reason,

                "escalation_required":
                    policy.escalation_required
            }


            # Step 5:
            # Execute only if policy allows

            if policy.is_allowed:

                execution = (
                    self.execution_engine
                    .execute(
                        db=db,
                        policy_evaluation_id=policy.id
                    )
                )

                result[
                    "execution_id"
                ] = execution.id

                result[
                    "execution_status"
                ] = (
                    execution.execution_status
                )

                result[
                    "result_message"
                ] = (
                    execution.result_message
                )

            else:

                result[
                    "execution_status"
                ] = "blocked"


            results.append(
                result
            )


        return {

            "merchant_id":
                merchant_id,

            "risk_cases_processed":
                len(results),

            "results":
                results
        }