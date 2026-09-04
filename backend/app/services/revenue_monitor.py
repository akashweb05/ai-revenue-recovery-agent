from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.models.revenue_risk import RevenueRiskCase


class RevenueMonitor:

    def scan_failed_payments(
        self,
        db: Session,
        merchant_id: int | None = None
    ):
        query = db.query(Payment).filter(
            Payment.status == "failed"
        )

        if merchant_id is not None:
            query = query.filter(
                Payment.merchant_id == merchant_id
            )

        failed_payments = query.all()

        created_cases = []

        for payment in failed_payments:

            existing_case = (
                db.query(RevenueRiskCase)
                .filter(
                    RevenueRiskCase.payment_id == payment.id
                )
                .first()
            )

            if existing_case:
                continue

            risk_score = self.calculate_risk_score(
                payment
            )

            risk_level = self.get_risk_level(
                risk_score
            )

            reason = self.build_reason(
                payment
            )

            risk_case = RevenueRiskCase(
                merchant_id=payment.merchant_id,
                customer_id=payment.customer_id,
                payment_id=payment.id,
                amount_at_risk=payment.amount,
                risk_score=risk_score,
                risk_level=risk_level,
                reason=reason,
                status="open"
            )

            db.add(risk_case)

            created_cases.append(
                risk_case
            )

        db.commit()

        for case in created_cases:
            db.refresh(case)

        return created_cases

    def calculate_risk_score(
        self,
        payment: Payment
    ) -> float:

        score = 50.0

        if payment.failure_code:
            score += 10

        if payment.amount >= 10000:
            score += 20
        elif payment.amount >= 5000:
            score += 10

        return min(score, 100)

    def get_risk_level(
        self,
        risk_score: float
    ) -> str:

        if risk_score >= 80:
            return "critical"

        if risk_score >= 60:
            return "high"

        if risk_score >= 40:
            return "medium"

        return "low"

    def build_reason(
        self,
        payment: Payment
    ) -> str:

        if payment.failure_reason:
            return payment.failure_reason

        if payment.failure_code:
            return (
                f"Payment failed with "
                f"code {payment.failure_code}"
            )

        return "Payment failed"