from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class RevenueRiskCase(Base):
    __tablename__ = "revenue_risk_cases"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False,
        unique=True,
        index=True
    )

    amount_at_risk = Column(
        Numeric(12, 2),
        nullable=False
    )

    risk_score = Column(
        Numeric(5, 2),
        nullable=False
    )

    risk_level = Column(
        String(20),
        nullable=False
    )

    reason = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        nullable=False,
        default="open",
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    payment = relationship("Payment")