from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.revenue_risk import RevenueRiskCase
from app.models.diagnosis import Diagnosis

from app.services.customer_history import (
    CustomerHistoryAnalyzer
)


class DiagnosisEngine:

    def __init__(self):
        self.history_analyzer = (
            CustomerHistoryAnalyzer()
        )

    def diagnose(
        self,
        db: Session,
        risk_case_id: int
    ) -> Diagnosis:

        risk_case = db.get(
            RevenueRiskCase,
            risk_case_id
        )

        if not risk_case:
            raise ValueError(
                "Revenue risk case not found"
            )

        existing_diagnosis = (
            db.query(Diagnosis)
            .filter(
                Diagnosis.risk_case_id == risk_case_id
            )
            .first()
        )

        if existing_diagnosis:
            return existing_diagnosis

        payment = db.get(
            Payment,
            risk_case.payment_id
        )

        history = self.history_analyzer.analyze(
            db=db,
            customer_id=payment.customer_id
        )

        diagnosis_result = self.determine_diagnosis(
            payment=payment,
            history=history
        )

        diagnosis = Diagnosis(
            risk_case_id=risk_case.id,
            diagnosis_type=diagnosis_result[
                "diagnosis_type"
            ],
            root_cause=diagnosis_result[
                "root_cause"
            ],
            explanation=diagnosis_result[
                "explanation"
            ],
            confidence_score=diagnosis_result[
                "confidence_score"
            ],
            recommended_action=diagnosis_result[
                "recommended_action"
            ]
        )

        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)

        return diagnosis

    def determine_diagnosis(
        self,
        payment: Payment,
        history: dict
    ) -> dict:

        failure_code = (
            payment.failure_code or ""
        ).upper()

        if failure_code == "CARD_DECLINED":

            if history["successful_payments"] > 0:

                return {
                    "diagnosis_type":
                        "temporary_payment_failure",

                    "root_cause":
                        "Bank declined an otherwise active payment method",

                    "explanation":
                        "The customer has successfully paid before, "
                        "which suggests the payment failure may be "
                        "temporary rather than permanent.",

                    "confidence_score": 85.0,

                    "recommended_action":
                        "retry"
                }

            return {
                "diagnosis_type":
                    "payment_method_issue",

                "root_cause":
                    "Card transaction declined by bank",

                "explanation":
                    "The customer has no successful payment history, "
                    "so the payment method may need to be changed.",

                "confidence_score": 75.0,

                "recommended_action":
                    "payment_link"
            }

        if failure_code in [
            "INSUFFICIENT_FUNDS",
            "LOW_BALANCE"
        ]:

            return {
                "diagnosis_type":
                    "temporary_funding_issue",

                "root_cause":
                    "Insufficient funds available",

                "explanation":
                    "The payment failed because sufficient funds were "
                    "not available at the time of the transaction.",

                "confidence_score": 90.0,

                "recommended_action":
                    "retry"
            }

        if failure_code in [
            "EXPIRED_CARD",
            "INVALID_CARD"
        ]:

            return {
                "diagnosis_type":
                    "payment_method_issue",

                "root_cause":
                    "Customer payment method requires replacement",

                "explanation":
                    "The existing payment method cannot be used for "
                    "recovery.",

                "confidence_score": 95.0,

                "recommended_action":
                    "payment_link"
            }

        return {
            "diagnosis_type":
                "unknown_failure",

            "root_cause":
                payment.failure_reason
                or "Unknown payment failure",

            "explanation":
                "There is not enough deterministic evidence to "
                "identify a precise cause.",

            "confidence_score": 50.0,

            "recommended_action":
                "reminder"
        }