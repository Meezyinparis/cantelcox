from sqlalchemy import Column, Integer, String, DateTime
from models.base import Base


class MobileLine(Base):
    __tablename__ = "mobile_lines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    msisdn = Column(String, unique=True, nullable=False)
    sim_number = Column(String, unique=True, nullable=False)
    line_status = Column(String, nullable=False, default="PENDING")
    activated_at = Column(DateTime, nullable=True)
