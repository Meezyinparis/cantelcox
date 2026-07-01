from db import get_sqlalchemy_session
from models.user_account import UserAccount


def get_user_account_by_id(account_id):
    """Get user account by ID"""

    session = get_sqlalchemy_session()

    result = session.query(UserAccount).filter_by(
        id=account_id
    ).all()

    if len(result):

        account = result[0]

        return {
            "id": account.id,
            "customer_id": account.customer_id,
            "email": account.email,
            "password_hash": account.password_hash,
        }

    return {}


def get_user_account_by_email(email):
    """Get user account by email"""

    session = get_sqlalchemy_session()

    result = session.query(UserAccount).filter_by(
        email=email
    ).all()

    if len(result):

        account = result[0]

        return {
            "id": account.id,
            "customer_id": account.customer_id,
            "email": account.email,
            "password_hash": account.password_hash,
        }

    return {}
