from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.revenue_risk import RevenueRiskCase
from app.models.recovery import Recovery
from app.models.action_execution import ActionExecution
from app.models.policy_evaluation import PolicyEvaluation
from app.models.payment import Payment
from app.models.customer import Customer
from app.models.diagnosis import Diagnosis
from app.models.payment_verification import PaymentVerification


class DashboardService:

    @staticmethod
    def _timestamp(value):
        if value is None:
            return None

        return value.isoformat()

    @staticmethod
    def _record(record, fields):
        if record is None:
            return None

        return {
            field: DashboardService._timestamp(
                getattr(record, field)
            ) if field.endswith("_at") else getattr(
                record,
                field,
                None
            )
            for field in fields
        }

    def _case_records(
        self,
        db: Session,
        risk_case: RevenueRiskCase
    ) -> dict:
        payment = db.get(
            Payment,
            risk_case.payment_id
        )
        customer = db.get(
            Customer,
            risk_case.customer_id
        )
        diagnosis = db.query(
            Diagnosis
        ).filter(
            Diagnosis.risk_case_id == risk_case.id
        ).first()
        recovery = db.query(
            Recovery
        ).filter(
            Recovery.risk_case_id == risk_case.id
        ).first()
        policy = None
        execution = None
        verification = None

        if recovery is not None:
            policy = db.query(
                PolicyEvaluation
            ).filter(
                PolicyEvaluation.recovery_id == recovery.id
            ).order_by(
                PolicyEvaluation.id.desc()
            ).first()

        if policy is not None:
            execution = db.query(
                ActionExecution
            ).filter(
                ActionExecution.policy_evaluation_id == policy.id
            ).first()

        if execution is not None:
            verification = db.query(
                PaymentVerification
            ).filter(
                PaymentVerification.execution_id == execution.id
            ).first()

        return {
            "risk_case": self._record(
                risk_case,
                [
                    "id",
                    "merchant_id",
                    "customer_id",
                    "payment_id",
                    "amount_at_risk",
                    "risk_score",
                    "risk_level",
                    "reason",
                    "status",
                    "created_at",
                    "updated_at"
                ]
            ),
            "payment": self._record(
                payment,
                [
                    "id",
                    "external_payment_id",
                    "merchant_id",
                    "customer_id",
                    "amount",
                    "currency",
                    "status",
                    "payment_method",
                    "failure_code",
                    "failure_reason",
                    "created_at",
                    "updated_at"
                ]
            ),
            "customer": self._record(
                customer,
                [
                    "id",
                    "merchant_id",
                    "external_customer_id",
                    "name",
                    "email",
                    "created_at"
                ]
            ),
            "diagnosis": self._record(
                diagnosis,
                [
                    "id",
                    "risk_case_id",
                    "diagnosis_type",
                    "root_cause",
                    "explanation",
                    "confidence_score",
                    "recommended_action",
                    "created_at"
                ]
            ),
            "recovery": self._record(
                recovery,
                [
                    "id",
                    "risk_case_id",
                    "diagnosis_id",
                    "recovery_probability",
                    "recommended_intervention",
                    "status",
                    "created_at"
                ]
            ),
            "policy": self._record(
                policy,
                [
                    "id",
                    "recovery_id",
                    "requested_action",
                    "is_allowed",
                    "reason",
                    "attempt_count",
                    "escalation_required",
                    "created_at"
                ]
            ),
            "execution": self._record(
                execution,
                [
                    "id",
                    "policy_evaluation_id",
                    "recovery_id",
                    "action",
                    "execution_status",
                    "result_message",
                    "external_reference",
                    "created_at"
                ]
            ),
            "verification": self._record(
                verification,
                [
                    "id",
                    "execution_id",
                    "recovery_id",
                    "payment_verified",
                    "verification_status",
                    "verification_message",
                    "created_at"
                ]
            )
        }

    def get_cases(
        self,
        db: Session,
        merchant_id: int | None = None
    ) -> list[dict]:
        query = db.query(
            RevenueRiskCase
        ).order_by(
            RevenueRiskCase.created_at.desc(),
            RevenueRiskCase.id.desc()
        )

        if merchant_id is not None:
            query = query.filter(
                RevenueRiskCase.merchant_id == merchant_id
            )

        cases = []

        for risk_case in query.all():
            records = self._case_records(
                db,
                risk_case
            )
            payment = records["payment"] or {}
            customer = records["customer"] or {}
            diagnosis = records["diagnosis"] or {}
            recovery = records["recovery"] or {}
            policy = records["policy"] or {}
            execution = records["execution"] or {}
            verification = records["verification"] or {}

            cases.append({
                "risk_case_id": risk_case.id,
                "payment_id": risk_case.payment_id,
                "merchant_id": risk_case.merchant_id,
                "customer_id": risk_case.customer_id,
                "customer_name": customer.get("name"),
                "customer_email": customer.get("email"),
                "amount_at_risk": float(
                    risk_case.amount_at_risk
                ),
                "payment_status": payment.get("status"),
                "payment_method": payment.get("payment_method"),
                "failure_code": payment.get("failure_code"),
                "failure_reason": payment.get("failure_reason"),
                "diagnosis_type": diagnosis.get("diagnosis_type"),
                "recovery_probability": (
                    float(recovery["recovery_probability"])
                    if recovery.get("recovery_probability")
                    is not None else None
                ),
                "recommended_action": recovery.get(
                    "recommended_intervention"
                ) or diagnosis.get("recommended_action"),
                "policy_allowed": policy.get("is_allowed"),
                "policy_reason": policy.get("reason"),
                "escalation_required": policy.get(
                    "escalation_required"
                ),
                "execution_id": execution.get("id"),
                "execution_status": execution.get(
                    "execution_status"
                ),
                "verification_status": verification.get(
                    "verification_status"
                ),
                "recovered": verification.get(
                    "payment_verified",
                    recovery.get("status") == "recovered"
                ),
                "created_at": self._timestamp(
                    risk_case.created_at
                )
            })

        return cases

    def get_case(
        self,
        db: Session,
        risk_case_id: int
    ) -> dict | None:
        risk_case = db.get(
            RevenueRiskCase,
            risk_case_id
        )

        if risk_case is None:
            return None

        return self._case_records(
            db,
            risk_case
        )

    def get_case_timeline(
        self,
        db: Session,
        risk_case_id: int
    ) -> dict | None:
        case = self.get_case(
            db,
            risk_case_id
        )

        if case is None:
            return None

        events = []
        payment = case["payment"]
        risk_case = case["risk_case"]
        diagnosis = case["diagnosis"]
        recovery = case["recovery"]
        policy = case["policy"]
        execution = case["execution"]
        verification = case["verification"]

        if payment is not None:
            events.append({
                "step": "payment_failed",
                "title": "Payment Failed",
                "description": payment.get("failure_reason"),
                "status": "completed",
                "timestamp": payment.get("created_at")
            })

        events.append({
            "step": "risk_detected",
            "title": "Revenue Risk Detected",
            "description": risk_case.get("reason"),
            "status": "completed",
            "timestamp": risk_case.get("created_at")
        })

        events.append({
            "step": "diagnosis",
            "title": "AI Diagnosis Completed",
            "description": diagnosis.get("diagnosis_type")
            if diagnosis else None,
            "status": "completed" if diagnosis else "pending",
            "timestamp": diagnosis.get("created_at")
            if diagnosis else None
        })

        events.append({
            "step": "recovery_recommendation",
            "title": "Recovery Action Recommended",
            "description": recovery.get(
                "recommended_intervention"
            ) if recovery else None,
            "status": "completed" if recovery else "pending",
            "timestamp": recovery.get("created_at")
            if recovery else None
        })

        events.append({
            "step": "policy",
            "title": "Policy Evaluation",
            "description": policy.get("reason") if policy else None,
            "status": (
                "allowed" if policy and policy.get("is_allowed")
                else "blocked" if policy else "pending"
            ),
            "timestamp": policy.get("created_at")
            if policy else None
        })

        events.append({
            "step": "execution",
            "title": "Action Executed",
            "description": execution.get("result_message")
            if execution else None,
            "status": execution.get("execution_status")
            if execution else "pending",
            "timestamp": execution.get("created_at")
            if execution else None
        })

        events.append({
            "step": "verification",
            "title": "Payment Verification",
            "description": verification.get("verification_message")
            if verification else None,
            "status": verification.get("verification_status")
            if verification else "pending",
            "timestamp": verification.get("created_at")
            if verification else None
        })

        return {
            "risk_case_id": risk_case_id,
            "events": events
        }

    def get_metrics(
        self,
        db: Session,
        merchant_id: int | None = None
    ) -> dict:

        risk_query = db.query(
            RevenueRiskCase
        )

        if merchant_id is not None:

            risk_query = risk_query.filter(
                RevenueRiskCase.merchant_id
                == merchant_id
            )

        risk_cases = risk_query.all()

        total_payments_at_risk = len(
            risk_cases
        )

        total_amount_at_risk = sum(
            float(case.amount_at_risk)
            for case in risk_cases
        )

        recovered_query = (
            db.query(Recovery)
            .join(
                RevenueRiskCase,
                Recovery.risk_case_id
                == RevenueRiskCase.id
            )
            .filter(
                Recovery.status == "recovered"
            )
        )

        if merchant_id is not None:

            recovered_query = (
                recovered_query.filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        recovered_cases = (
            recovered_query.all()
        )

        total_recovered = len(
            recovered_cases
        )

        total_amount_recovered = sum(
            float(
                db.get(
                    RevenueRiskCase,
                    recovery.risk_case_id
                ).amount_at_risk
            )
            for recovery in recovered_cases
        )

        recovery_rate = 0

        if total_payments_at_risk > 0:

            recovery_rate = (
                total_recovered
                / total_payments_at_risk
            ) * 100

        execution_query = (
            db.query(ActionExecution)
        )

        if merchant_id is not None:

            execution_query = (
                execution_query
                .join(
                    Recovery,
                    ActionExecution.recovery_id
                    == Recovery.id
                )
                .join(
                    RevenueRiskCase,
                    Recovery.risk_case_id
                    == RevenueRiskCase.id
                )
                .filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        actions_executed = (
            execution_query.count()
        )

        policy_block_query = (
            db.query(PolicyEvaluation)
            .filter(
                PolicyEvaluation.is_allowed
                == False
            )
        )

        if merchant_id is not None:

            policy_block_query = (
                policy_block_query
                .join(
                    Recovery,
                    PolicyEvaluation.recovery_id
                    == Recovery.id
                )
                .join(
                    RevenueRiskCase,
                    Recovery.risk_case_id
                    == RevenueRiskCase.id
                )
                .filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        policy_blocks = (
            policy_block_query.count()
        )

        escalation_query = (
            db.query(PolicyEvaluation)
            .filter(
                PolicyEvaluation.escalation_required
                == True
            )
        )

        if merchant_id is not None:

            escalation_query = (
                escalation_query
                .join(
                    Recovery,
                    PolicyEvaluation.recovery_id
                    == Recovery.id
                )
                .join(
                    RevenueRiskCase,
                    Recovery.risk_case_id
                    == RevenueRiskCase.id
                )
                .filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        escalations = (
            escalation_query.count()
        )

        


        return {

            "merchant_id": merchant_id,

            "total_payments_at_risk":
                total_payments_at_risk,

            "total_amount_at_risk":
                round(
                    total_amount_at_risk,
                    2
                ),

            "total_recovered":
                total_recovered,

            "total_amount_recovered":
                round(
                    total_amount_recovered,
                    2
                ),

            "recovery_rate":
                round(
                    recovery_rate,
                    2
                ),

            "actions_executed":
                actions_executed,

            "policy_blocks":
                policy_blocks,

            "escalations":
                escalations
        }

    def get_summary(
        self,
        db: Session,
        merchant_id: int | None = None
    ) -> dict:

        risk_query = db.query(
            RevenueRiskCase
        )

        if merchant_id is not None:

            risk_query = risk_query.filter(
                RevenueRiskCase.merchant_id
                == merchant_id
            )

        risk_cases = risk_query.all()

        total_cases = len(
            risk_cases
        )

        total_amount_at_risk = sum(
            float(case.amount_at_risk)
            for case in risk_cases
        )

        recovery_query = (
            db.query(Recovery)
            .join(
                RevenueRiskCase,
                Recovery.risk_case_id
                == RevenueRiskCase.id
            )
        )

        if merchant_id is not None:

            recovery_query = (
                recovery_query.filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        recoveries = recovery_query.all()

        recovered_cases = len([
            recovery
            for recovery in recoveries
            if recovery.status == "recovered"
        ])

        pending_cases = len([
            recovery
            for recovery in recoveries
            if recovery.status == "pending"
        ])

        executed_cases = len([
            recovery
            for recovery in recoveries
            if recovery.status == "executed"
        ])

        verification_failed_cases = len([
            recovery
            for recovery in recoveries
            if recovery.status == "verification_failed"
        ])

        recovered_amount = 0.0

        for recovery in recoveries:

            if recovery.status == "recovered":

                risk_case = db.get(
                    RevenueRiskCase,
                    recovery.risk_case_id
                )

                if risk_case:

                    recovered_amount += float(
                        risk_case.amount_at_risk
                    )

        recovery_rate = 0.0

        if total_cases > 0:

            recovery_rate = (
                recovered_cases
                / total_cases
            ) * 100

        retry_count = len([
            recovery
            for recovery in recoveries
            if recovery.recommended_intervention == "retry"
        ])

        reminder_count = len([
            recovery
            for recovery in recoveries
            if recovery.recommended_intervention == "reminder"
        ])

        payment_link_count = len([
            recovery
            for recovery in recoveries
            if recovery.recommended_intervention == "payment_link"
        ])

        policy_query = (
            db.query(PolicyEvaluation)
            .join(
                Recovery,
                PolicyEvaluation.recovery_id
                == Recovery.id
            )
            .join(
                RevenueRiskCase,
                Recovery.risk_case_id
                == RevenueRiskCase.id
            )
        )

        if merchant_id is not None:

            policy_query = (
                policy_query.filter(
                    RevenueRiskCase.merchant_id
                    == merchant_id
                )
            )

        policy_evaluations = policy_query.all()

        blocked_actions = len([
            policy
            for policy in policy_evaluations
            if not policy.is_allowed
        ])

        escalated_cases = len([
            policy
            for policy in policy_evaluations
            if policy.escalation_required
        ])

        return {
            "merchant_id": merchant_id,
            "overview": {
                "total_cases": total_cases,
                "total_amount_at_risk": round(
                    total_amount_at_risk,
                    2
                ),
                "recovered_cases": recovered_cases,
                "recovered_amount": round(
                    recovered_amount,
                    2
                ),
                "recovery_rate": round(
                    recovery_rate,
                    2
                )
            },
            "case_status": {
                "pending": pending_cases,
                "executed": executed_cases,
                "recovered": recovered_cases,
                "verification_failed": verification_failed_cases
            },
            "interventions": {
                "retry": retry_count,
                "reminder": reminder_count,
                "payment_link": payment_link_count
            },
            "policy": {
                "blocked_actions": blocked_actions,
                "escalated_cases": escalated_cases
            }
        }

    