from datetime import datetime, timedelta
from models.mfa_otp import MfaOtp
from db import get_sqlalchemy_session


def add_mfa_otp(user_account_id: int, otp_code: str, purpose: str = "LOGIN"):
    """Insert MFA OTP in MySQL"""

    if not user_account_id or not otp_code:
        raise ValueError("Cannot create MFA OTP.")

    session = get_sqlalchemy_session()

    try:
        otp = MfaOtp(
            user_account_id=user_account_id,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=datetime.now() + timedelta(minutes=5),
            used=False
        )

        session.add(otp)
        session.flush()
        session.commit()

        return otp.id

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()


def mark_otp_as_used(otp_id: int):
    """Mark OTP as used"""

    session = get_sqlalchemy_session()

    try:
        otp = session.query(MfaOtp).filter(MfaOtp.id == otp_id).first()

        if otp:
            otp.used = True
            session.commit()
            return 1

        return 0

    except Exception as e:
        session.rollback()
        raise e

    finally:
        session.close()