from sqlalchemy.orm import Session

from app.models.revenue_risk import RevenueRiskCase
from app.models.diagnosis import Diagnosis
from app.models.recovery import Recovery
from app.models.payment import Payment

from app.services.customer_history import (
    CustomerHistoryAnalyzer
)


class RecoveryEngine:

    def __init__(self):

        self.history_analyzer = (
            CustomerHistoryAnalyzer()
        )

    def analyze(
        self,
        db: Session,
        risk_case_id: int
    ) -> Recovery:

        risk_case = db.get(
            RevenueRiskCase,
            risk_case_id
        )

        if not risk_case:

            raise ValueError(
                "Revenue risk case not found"
            )

        existing_recovery = (
            db.query(Recovery)
            .filter(
                Recovery.risk_case_id == risk_case_id
            )
            .first()
        )

        if existing_recovery:
            return existing_recovery

        diagnosis = (
            db.query(Diagnosis)
            .filter(
                Diagnosis.risk_case_id == risk_case_id
            )
            .first()
        )

        if not diagnosis:

            raise ValueError(
                "Diagnosis not found for risk case"
            )

        payment = db.get(
            Payment,
            risk_case.payment_id
        )

        history = self.history_analyzer.analyze(
            db=db,
            customer_id=payment.customer_id
        )

        probability = (
            self.calculate_probability(
                payment=payment,
                diagnosis=diagnosis,
                history=history
            )
        )

        intervention = (
            self.select_intervention(
                probability=probability,
                diagnosis=diagnosis
            )
        )

        recovery = Recovery(
            risk_case_id=risk_case.id,
            diagnosis_id=diagnosis.id,
            recovery_probability=probability,
            recommended_intervention=intervention,
            status="pending"
        )

        db.add(recovery)
        db.commit()
        db.refresh(recovery)

        return recovery

    def calculate_probability(
        self,
        payment: Payment,
        diagnosis: Diagnosis,
        history: dict
    ) -> float:

        score = 50.0

        # Customer payment history

        success_rate = (
            history["success_rate"]
        )

        if success_rate >= 90:
            score += 25

        elif success_rate >= 70:
            score += 15

        elif success_rate >= 50:
            score += 5

        else:
            score -= 10


        # Failure type

        failure_code = (
            payment.failure_code or ""
        ).upper()

        if failure_code in [
            "CARD_DECLINED",
            "INSUFFICIENT_FUNDS",
            "LOW_BALANCE"
        ]:
            score += 15

        elif failure_code in [
            "EXPIRED_CARD",
            "INVALID_CARD"
        ]:
            score -= 15


        # Diagnosis confidence

        confidence = float(
            diagnosis.confidence_score
        )

        if confidence >= 90:
            score += 10

        elif confidence >= 75:
            score += 5


        # Repeat failure history

        failed_payments = (
            history["failed_payments"]
        )

        if failed_payments >= 5:
            score -= 20

        elif failed_payments >= 3:
            score -= 10


        # Higher-value payments can be harder to recover

        amount = float(
            payment.amount
        )

        if amount >= 100000:
            score -= 10

        elif amount >= 50000:
            score -= 5


        # Keep between 0 and 100

        return max(
            0,
            min(
                100,
                round(score, 2)
            )
        )

    def select_intervention(
        self,
        probability: float,
        diagnosis: Diagnosis
    ) -> str:

        recommended_action = (
            diagnosis.recommended_action
        )

        # High probability
        if probability >= 75:

            if recommended_action == "retry":
                return "retry"

            return recommended_action


        # Medium probability
        if probability >= 50:

            if recommended_action == "retry":
                return "reminder"

            return recommended_action


        # Low probability
        return "payment_link"