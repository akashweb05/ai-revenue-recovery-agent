from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database.connection import Base


class PaymentVerification(Base):

    __tablename__ = "payment_verifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    execution_id = Column(
        Integer,
        ForeignKey("action_executions.id"),
        nullable=False,
        unique=True,
        index=True
    )

    recovery_id = Column(
        Integer,
        ForeignKey("recoveries.id"),
        nullable=False,
        index=True
    )

    payment_verified = Column(
        Boolean,
        nullable=False,
        default=False
    )

    verification_status = Column(
        String(50),
        nullable=False
    )

    verification_message = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )