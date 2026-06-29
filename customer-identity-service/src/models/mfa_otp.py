from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from models.base import Base


class MfaOtp(Base):
    __tablename__ = "mfa_otps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_account_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    otp_code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, nullable=False, default=False)