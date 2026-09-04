import uuid

from sqlalchemy.orm import Session

from app.models.policy_evaluation import (
    PolicyEvaluation
)

from app.models.recovery import Recovery

from app.models.action_execution import (
    ActionExecution
)


class ExecutionEngine:

    def execute(
        self,
        db: Session,
        policy_evaluation_id: int
    ) -> ActionExecution:

        policy = db.get(
            PolicyEvaluation,
            policy_evaluation_id
        )

        if not policy:

            raise ValueError(
                "Policy evaluation not found"
            )

        existing_execution = (
            db.query(ActionExecution)
            .filter(
                ActionExecution.policy_evaluation_id
                == policy_evaluation_id
            )
            .first()
        )

        if existing_execution:

            return existing_execution

        if not policy.is_allowed:

            raise ValueError(
                "Action blocked by policy engine"
            )

        recovery = db.get(
            Recovery,
            policy.recovery_id
        )

        if not recovery:

            raise ValueError(
                "Recovery record not found"
            )

        action = policy.requested_action

        result = self.perform_action(
            action=action,
            recovery=recovery
        )

        execution = ActionExecution(

            policy_evaluation_id=policy.id,

            recovery_id=recovery.id,

            action=action,

            execution_status=result[
                "execution_status"
            ],

            result_message=result[
                "result_message"
            ],

            external_reference=result[
                "external_reference"
            ]
        )

        db.add(execution)

        # Update recovery workflow state
        recovery.status = (
            "executed"
            if result["execution_status"] == "success"
            else "failed"
        )

        db.commit()

        db.refresh(execution)

        return execution


    def perform_action(
        self,
        action: str,
        recovery: Recovery
    ) -> dict:

        if action == "retry":

            return {
                "execution_status": "success",

                "result_message":
                    "Payment retry request submitted successfully",

                "external_reference":
                    f"retry_{uuid.uuid4().hex[:12]}"
            }


        if action == "reminder":

            return {
                "execution_status": "success",

                "result_message":
                    "Payment reminder sent successfully",

                "external_reference":
                    f"reminder_{uuid.uuid4().hex[:12]}"
            }


        if action == "payment_link":

            return {
                "execution_status": "success",

                "result_message":
                    "Payment link generated successfully",

                "external_reference":
                    f"plink_{uuid.uuid4().hex[:12]}"
            }


        return {
            "execution_status": "failed",

            "result_message":
                "Unknown action",

            "external_reference": None
        }