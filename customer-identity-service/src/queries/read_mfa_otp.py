from datetime import datetime
from db import get_sqlalchemy_session
from models.mfa_otp import MfaOtp


def get_valid_otp(user_account_id: int, otp_code: str):
    """Get valid OTP by user account ID and code"""

    session = get_sqlalchemy_session()

    result = session.query(MfaOtp).filter(
        MfaOtp.user_account_id == user_account_id,
        MfaOtp.otp_code == otp_code,
        MfaOtp.used == False,
        MfaOtp.expires_at > datetime.now()
    ).all()

    if len(result):
        otp = result[0]

        return {
            "id": otp.id,
            "user_account_id": otp.user_account_id,
            "otp_code": otp.otp_code,
            "purpose": otp.purpose,
            "expires_at": str(otp.expires_at),
            "used": otp.used
        }

    return {}
