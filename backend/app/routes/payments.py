from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models.customer import Customer
from app.models.merchant import Merchant
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse


router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"]
)


@router.post(
    "/",
    response_model=PaymentResponse
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    merchant = db.get(
        Merchant,
        payment_data.merchant_id
    )

    if not merchant:
        raise HTTPException(
            status_code=404,
            detail="Merchant not found"
        )

    customer = db.get(
        Customer,
        payment_data.customer_id
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    payment = Payment(
        merchant_id=payment_data.merchant_id,
        customer_id=payment_data.customer_id,
        external_payment_id=payment_data.external_payment_id,
        amount=payment_data.amount,
        currency=payment_data.currency,
        status=payment_data.status,
        payment_method=payment_data.payment_method,
        failure_code=payment_data.failure_code,
        failure_reason=payment_data.failure_reason
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment