from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import Base, engine
from app.models.merchant import Merchant
from app.models.customer import Customer
from app.models.payment import Payment
from app.routes.payments import router as payment_router
from app.models.revenue_risk import RevenueRiskCase
from app.routes.risk import router as risk_router
from app.models.diagnosis import Diagnosis
from app.routes.diagnosis import (router as diagnosis_router)
from app.models.recovery import Recovery
from app.routes.recovery import (router as recovery_router)
from app.models.policy_evaluation import PolicyEvaluation
from app.routes.policy import (router as policy_router)
from app.models.action_execution import ActionExecution
from app.routes.execution import (router as execution_router)
from app.models.payment_verification import PaymentVerification
from app.routes.verification import (router as verification_router)
from app.routes.orchestrator import (router as orchestrator_router)
from app.routes.dashboard import router as dashboard_router
from app.routes import demo
from app.routes import batch_demo

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Revenue Recovery Agent",
    description="AI-powered revenue recovery system",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(payment_router)
app.include_router(risk_router)
app.include_router(diagnosis_router)
app.include_router(recovery_router)
app.include_router(policy_router)
app.include_router(execution_router)
app.include_router(verification_router)
app.include_router(orchestrator_router)
app.include_router(dashboard_router)
app.include_router(demo.router)
app.include_router(batch_demo.router)

@app.get("/")
def root():
    return {
        "message": "Revenue Recovery Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }