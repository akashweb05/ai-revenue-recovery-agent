from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey
)

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Recovery(Base):
    __tablename__ = "recoveries"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    risk_case_id = Column(
        Integer,
        ForeignKey("revenue_risk_cases.id"),
        nullable=False,
        unique=True,
        index=True
    )

    diagnosis_id = Column(
        Integer,
        ForeignKey("diagnoses.id"),
        nullable=False,
        unique=True,
        index=True
    )

    recovery_probability = Column(
        Numeric(5, 2),
        nullable=False
    )

    recommended_intervention = Column(
        String(100),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="pending"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    risk_case = relationship(
        "RevenueRiskCase"
    )

    diagnosis = relationship(
        "Diagnosis"
    )