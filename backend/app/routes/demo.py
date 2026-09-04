from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db

from app.services.demo_data_generator import (
    DemoDataGenerator
)


router = APIRouter(

    prefix="/api/demo",

    tags=["Demo Data"]
)


@router.post("/generate")
def generate_demo_data(

    merchant_id: int = Query(
        default=1
    ),

    customer_count: int = Query(
        default=10,
        ge=1,
        le=100
    ),

    payments_per_customer: int = Query(
        default=5,
        ge=1,
        le=50
    ),

    db: Session = Depends(get_db)
):

    generator = DemoDataGenerator()

    result = generator.generate(

        db=db,

        merchant_id=merchant_id,

        customer_count=customer_count,

        payments_per_customer=
            payments_per_customer
    )

    return result