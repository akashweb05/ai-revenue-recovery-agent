from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.batch_demo_service import (
    BatchDemoService
)


router = APIRouter(

    prefix="/api/batch",

    tags=[
        "End-to-End Demo"
    ]
)


@router.post("/process")
def process_batch(

    merchant_id: int | None = None,

    db: Session = Depends(
        get_db
    )
):

    service = BatchDemoService()

    try:

        return service.process(

            db=db,

            merchant_id=
                merchant_id
        )

    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)
        )