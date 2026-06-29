from sqlalchemy import Column, Integer, String, Boolean, DECIMAL
from models.base import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    monthly_price = Column(DECIMAL(10, 2), nullable=False)
    data_limit_gb = Column(Integer)
    voice_minutes = Column(Integer)
    sms_limit = Column(Integer)
    active = Column(Boolean, nullable=False, default=True)