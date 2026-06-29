from models.customer import Customer
from db import get_sqlalchemy_session


def add_customer(first_name: str, last_name: str, email: str, phone_number: str):
    """Insert customer in MySQL"""

    if not first_name or not last_name or not email or not phone_number:
        raise ValueError(
            "Cannot create customer. Missing required information."
        )

    session = get_sqlalchemy_session()

    try:
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number
        )

        session.add(customer)
        session.flush()
        session.commit()

        return customer.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_customer(customer_id: int):
    """Delete customer in MySQL"""

    session = get_sqlalchemy_session()

    try:
        customer = session.query(Customer).filter(
            Customer.id == customer_id
        ).first()

        if customer:
            session.delete(customer)
            session.commit()
            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
