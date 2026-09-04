from pydantic import BaseModel


class VerificationCreate(BaseModel):

    payment_success: bool