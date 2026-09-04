from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.revenue_risk import RevenueRiskCase
from app.models.recovery import Recovery

from app.services.revenue_monitor import RevenueMonitor
from app.services.diagnosis_engine import DiagnosisEngine
from app.services.recovery_engine import RecoveryEngine
from app.services.policy_engine import PolicyEngine
from app.services.execution_engine import ExecutionEngine
from app.services.verification_engine import VerificationEngine


class BatchDemoService:

    def __init__(self):

        self.revenue_monitor = RevenueMonitor()

        self.diagnosis_engine = DiagnosisEngine()

        self.recovery_engine = RecoveryEngine()

        self.policy_engine = PolicyEngine()

        self.execution_engine = ExecutionEngine()

        self.verification_engine = VerificationEngine()


    def process(
        self,
        db: Session,
        merchant_id: int | None = None
    ) -> dict:

        # ----------------------------------------
        # STEP 1
        # Detect failed payments and create
        # revenue risk cases
        # ----------------------------------------

        created_risk_cases = (
            self.revenue_monitor
            .scan_failed_payments(
                db=db,
                merchant_id=merchant_id
            )
        )

        # ----------------------------------------
        # Get all open risk cases
        # ----------------------------------------

        risk_query = (
            db.query(RevenueRiskCase)
            .filter(
                RevenueRiskCase.status == "open"
            )
        )

        if merchant_id is not None:

            risk_query = (
                risk_query.filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        risk_cases = risk_query.all()

        # ----------------------------------------
        # Summary counters
        # ----------------------------------------

        total_amount_at_risk = 0.0

        cases_processed = 0

        actions_executed = 0

        actions_blocked = 0

        escalated_cases = 0

        successful_recoveries = 0

        recovered_amount = 0.0

        results = []


        # ----------------------------------------
        # STEP 2
        # Process every risk case
        # ----------------------------------------

        for risk_case in risk_cases:

            payment = db.get(
                Payment,
                risk_case.payment_id
            )

            if not payment:
                continue

            total_amount_at_risk += float(
                risk_case.amount_at_risk
            )

            try:

                # --------------------------------
                # STEP 3
                # AI Diagnosis
                # --------------------------------

                diagnosis = (
                    self.diagnosis_engine
                    .diagnose(
                        db=db,
                        risk_case_id=risk_case.id
                    )
                )


                # --------------------------------
                # STEP 4
                # Recovery Analysis
                # --------------------------------

                recovery = (
                    self.recovery_engine
                    .analyze(
                        db=db,
                        risk_case_id=risk_case.id
                    )
                )


                # --------------------------------
                # STEP 5
                # Policy Evaluation
                # --------------------------------

                policy = (
                    self.policy_engine
                    .evaluate(
                        db=db,
                        recovery_id=recovery.id
                    )
                )


                # --------------------------------
                # Policy blocked
                # --------------------------------

                if not policy.is_allowed:

                    actions_blocked += 1

                    if policy.escalation_required:

                        escalated_cases += 1

                    results.append({

                        "risk_case_id":
                            risk_case.id,

                        "payment_id":
                            payment.id,

                        "amount_at_risk":
                            float(
                                risk_case.amount_at_risk
                            ),

                        "diagnosis_type":
                            diagnosis.diagnosis_type,

                        "recovery_probability":
                            float(
                                recovery.recovery_probability
                            ),

                        "recommended_action":
                            recovery
                            .recommended_intervention,

                        "policy_allowed":
                            False,

                        "policy_reason":
                            policy.reason,

                        "escalation_required":
                            policy
                            .escalation_required,

                        "execution_status":
                            "blocked",

                        "verification_status":
                            None,

                        "recovered":
                            False
                    })

                    continue


                # --------------------------------
                # STEP 6
                # Execute Action
                # --------------------------------

                execution = (
                    self.execution_engine
                    .execute(
                        db=db,
                        policy_evaluation_id=
                            policy.id
                    )
                )

                actions_executed += 1


                # --------------------------------
                # STEP 7
                # Simulate payment outcome
                #
                # High recovery probability
                # = more likely success
                # --------------------------------

                payment_success = (
                    float(
                        recovery
                        .recovery_probability
                    )
                    >= 60
                )


                # --------------------------------
                # STEP 8
                # Verify Recovery
                # --------------------------------

                verification = (
                    self.verification_engine
                    .verify(
                        db=db,
                        execution_id=
                            execution.id,

                        payment_success=
                            payment_success
                    )
                )


                recovered = (
                    verification
                    .payment_verified
                )

                if recovered:

                    successful_recoveries += 1

                    recovered_amount += float(
                        payment.amount
                    )


                # --------------------------------
                # STEP 9
                # Close risk case if recovered
                # --------------------------------

                if recovered:

                    risk_case.status = (
                        "recovered"
                    )

                    db.commit()


                results.append({

                    "risk_case_id":
                        risk_case.id,

                    "payment_id":
                        payment.id,

                    "amount_at_risk":
                        float(
                            risk_case.amount_at_risk
                        ),

                    "diagnosis_type":
                        diagnosis.diagnosis_type,

                    "recovery_probability":
                        float(
                            recovery
                            .recovery_probability
                        ),

                    "recommended_action":
                        recovery
                        .recommended_intervention,

                    "policy_allowed":
                        True,

                    "policy_reason":
                        policy.reason,

                    "escalation_required":
                        policy
                        .escalation_required,

                    "execution_id":
                        execution.id,

                    "execution_status":
                        execution.execution_status,

                    "verification_status":
                        verification
                        .verification_status,

                    "recovered":
                        recovered
                })

                cases_processed += 1


            except ValueError as error:

                results.append({

                    "risk_case_id":
                        risk_case.id,

                    "payment_id":
                        payment.id,

                    "error":
                        str(error)
                })


        # ----------------------------------------
        # Final Summary
        # ----------------------------------------

        recovery_rate = 0.0

        if total_amount_at_risk > 0:

            recovery_rate = (
                recovered_amount
                / total_amount_at_risk
            ) * 100


        return {

            "merchant_id":
                merchant_id,

            "new_risk_cases_detected":
                len(created_risk_cases),

            "risk_cases_found":
                len(risk_cases),

            "cases_processed":
                cases_processed,

            "actions_executed":
                actions_executed,

            "actions_blocked":
                actions_blocked,

            "escalated_cases":
                escalated_cases,

            "successful_recoveries":
                successful_recoveries,

            "total_amount_at_risk":
                round(
                    total_amount_at_risk,
                    2
                ),

            "recovered_amount":
                round(
                    recovered_amount,
                    2
                ),

            "money_recovery_rate":
                round(
                    recovery_rate,
                    2
                ),

            "results":
                results
        }