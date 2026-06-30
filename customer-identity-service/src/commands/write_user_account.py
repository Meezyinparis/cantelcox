import bcrypt
from models.user_account import UserAccount
from db import get_sqlalchemy_session


def add_user_account(customer_id: int, email: str, password: str):
    """Insert user account in MySQL"""

    if not customer_id or not email or not password:
        raise ValueError("Cannot create user account.")

    session = get_sqlalchemy_session()

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:

        account = UserAccount(
            customer_id=customer_id,
            email=email,
            password_hash=password
        )

        session.add(account)
        session.flush()
        session.commit()

        return account.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def delete_user_account(account_id: int):
    """Delete user account"""

    session = get_sqlalchemy_session()

    try:

        account = session.query(UserAccount).filter(
            UserAccount.id == account_id
        ).first()

        if account:
            session.delete(account)
            session.commit()
            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()
