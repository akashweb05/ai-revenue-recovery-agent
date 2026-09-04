from sqlalchemy.orm import Session

from app.models.payment import Payment


class CustomerHistoryAnalyzer:

    def analyze(
        self,
        db: Session,
        customer_id: int
    ) -> dict:

        payments = (
            db.query(Payment)
            .filter(
                Payment.customer_id == customer_id
            )
            .all()
        )

        total_payments = len(payments)

        successful_payments = len([
            payment
            for payment in payments
            if payment.status == "success"
        ])

        failed_payments = len([
            payment
            for payment in payments
            if payment.status == "failed"
        ])

        total_success_amount = sum(
            payment.amount
            for payment in payments
            if payment.status == "success"
        )

        success_rate = 0

        if total_payments > 0:
            success_rate = (
                successful_payments
                / total_payments
            ) * 100

        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "failed_payments": failed_payments,
            "success_rate": round(success_rate, 2),
            "total_success_amount": float(
                total_success_amount
            )
        }