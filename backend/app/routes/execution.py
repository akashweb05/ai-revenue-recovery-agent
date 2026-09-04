from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.execution_engine import (
    ExecutionEngine
)


router = APIRouter(
    prefix="/api/execution",
    tags=["Execution Engine"]
)


@router.post("/{policy_evaluation_id}")
def execute_action(
    policy_evaluation_id: int,
    db: Session = Depends(get_db)
):

    engine = ExecutionEngine()

    try:

        execution = engine.execute(
            db=db,
            policy_evaluation_id=policy_evaluation_id
        )

        return {
            "id": execution.id,

            "policy_evaluation_id":
                execution.policy_evaluation_id,

            "recovery_id":
                execution.recovery_id,

            "action":
                execution.action,

            "execution_status":
                execution.execution_status,

            "result_message":
                execution.result_message,

            "external_reference":
                execution.external_reference
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )