from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database.connection import Base


class PolicyEvaluation(Base):

    __tablename__ = "policy_evaluations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    recovery_id = Column(
        Integer,
        ForeignKey("recoveries.id"),
        nullable=False,
        index=True
    )

    requested_action = Column(
        String(100),
        nullable=False
    )

    is_allowed = Column(
        Boolean,
        nullable=False
    )

    reason = Column(
        Text,
        nullable=False
    )

    attempt_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    escalation_required = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )