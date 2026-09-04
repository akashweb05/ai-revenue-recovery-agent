from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

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

    diagnosis_type = Column(
        String(100),
        nullable=False
    )

    root_cause = Column(
        String(255),
        nullable=False
    )

    explanation = Column(
        Text,
        nullable=False
    )

    confidence_score = Column(
        Numeric(5, 2),
        nullable=False
    )

    recommended_action = Column(
        String(100),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    risk_case = relationship(
        "RevenueRiskCase"
    )