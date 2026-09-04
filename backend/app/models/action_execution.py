from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func

from app.database.connection import Base


class ActionExecution(Base):

    __tablename__ = "action_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    policy_evaluation_id = Column(
        Integer,
        ForeignKey("policy_evaluations.id"),
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

    action = Column(
        String(100),
        nullable=False
    )

    execution_status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    result_message = Column(
        Text,
        nullable=True
    )

    external_reference = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )