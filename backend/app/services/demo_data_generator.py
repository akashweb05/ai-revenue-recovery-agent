import random
import uuid

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.payment import Payment
from app.models.merchant import Merchant


class DemoDataGenerator:

    def generate(
        self,
        db: Session,
        merchant_id: int,
        customer_count: int = 10,
        payments_per_customer: int = 5
    ) -> dict:

        # ----------------------------------------
        # Step 1: Ensure merchant exists
        # ----------------------------------------

        merchant_created = False

        merchant = db.get(
            Merchant,
            merchant_id
        )

        if not merchant:

            merchant = Merchant(
                id=merchant_id,

                name=(
                    f"Demo Merchant "
                    f"{merchant_id}"
                ),

                email=(
                    f"demo_merchant_"
                    f"{merchant_id}@example.com"
                )
            )

            db.add(merchant)

            merchant_created = True

            db.commit()

            db.refresh(merchant)

        created_customers = []
        created_payments = []

        # ----------------------------------------
        # Step 2: Create customers
        # ----------------------------------------

        for index in range(
            customer_count
        ):

            customer = Customer(

                merchant_id=merchant.id,

                name=(
                    f"Demo Customer "
                    f"{index + 1}"
                ),

                email=(
                    f"demo_customer_"
                    f"{uuid.uuid4().hex[:8]}"
                    f"@example.com"
                )
            )

            db.add(customer)

            created_customers.append(
                customer
            )

        # ----------------------------------------
        # Step 3: Save customers first
        # ----------------------------------------

        db.commit()

        # Refresh customers so they receive
        # their database-generated IDs

        for customer in created_customers:

            db.refresh(customer)

        # ----------------------------------------
        # Step 4: Demo payment configuration
        # ----------------------------------------

        payment_methods = [
            "card",
            "upi",
            "netbanking"
        ]

        amounts = [
            500,
            1000,
            1500,
            2500,
            5000,
            7500,
            10000,
            15000,
            25000
        ]

        failure_types = [

            {
                "failure_code":
                    "CARD_DECLINED",

                "failure_reason":
                    "Bank declined the transaction"
            },

            {
                "failure_code":
                    "INSUFFICIENT_FUNDS",

                "failure_reason":
                    "Insufficient funds available"
            },

            {
                "failure_code":
                    "LOW_BALANCE",

                "failure_reason":
                    "Customer account has insufficient balance"
            },

            {
                "failure_code":
                    "EXPIRED_CARD",

                "failure_reason":
                    "Customer payment card has expired"
            },

            {
                "failure_code":
                    "INVALID_CARD",

                "failure_reason":
                    "Invalid payment card details"
            }
        ]

        # ----------------------------------------
        # Step 5: Create payments
        # ----------------------------------------

        for customer in created_customers:

            for _ in range(
                payments_per_customer
            ):

                is_success = (
                    random.random() < 0.55
                )

                amount = random.choice(
                    amounts
                )

                payment_method = (
                    random.choice(
                        payment_methods
                    )
                )

                if is_success:

                    payment = Payment(

                        merchant_id=
                            merchant.id,

                        customer_id=
                            customer.id,

                        external_payment_id=(
                            f"demo_"
                            f"{uuid.uuid4().hex[:12]}"
                        ),

                        amount=
                            amount,

                        currency=
                            "INR",

                        status=
                            "success",

                        payment_method=
                            payment_method,

                        failure_code=
                            None,

                        failure_reason=
                            None
                    )

                else:

                    failure = random.choice(
                        failure_types
                    )

                    payment = Payment(

                        merchant_id=
                            merchant.id,

                        customer_id=
                            customer.id,

                        external_payment_id=(
                            f"demo_"
                            f"{uuid.uuid4().hex[:12]}"
                        ),

                        amount=
                            amount,

                        currency=
                            "INR",

                        status=
                            "failed",

                        payment_method=
                            payment_method,

                        failure_code=
                            failure[
                                "failure_code"
                            ],

                        failure_reason=
                            failure[
                                "failure_reason"
                            ]
                    )

                db.add(payment)

                created_payments.append(
                    payment
                )

        # ----------------------------------------
        # Step 6: Save all payments
        # ----------------------------------------

        db.commit()

        # ----------------------------------------
        # Step 7: Return generation summary
        # ----------------------------------------

        successful_payments = len([
            payment
            for payment in created_payments
            if payment.status
            == "success"
        ])

        failed_payments = len([
            payment
            for payment in created_payments
            if payment.status
            == "failed"
        ])

        return {

            "merchant_id":
                merchant.id,

            "merchant_created":
                merchant_created,

            "customers_created":
                len(
                    created_customers
                ),

            "payments_created":
                len(
                    created_payments
                ),

            "successful_payments":
                successful_payments,

            "failed_payments":
                failed_payments
        }