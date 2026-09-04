from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    merchant_id: int
    customer_id: int

    external_payment_id: str | None = None

    amount: Decimal = Field(
        gt=0,
        decimal_places=2
    )

    currency: str = "INR"

    status: str

    payment_method: str | None = None

    failure_code: str | None = None

    failure_reason: str | None = None


class PaymentResponse(BaseModel):
    id: int
    merchant_id: int
    customer_id: int

    external_payment_id: str | None

    amount: Decimal
    currency: str
    status: str

    payment_method: str | None
    failure_code: str | None
    failure_reason: str | None

    class Config:
        from_attributes = True