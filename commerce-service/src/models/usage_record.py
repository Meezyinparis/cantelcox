from sqlalchemy import Column, Integer, DECIMAL, String, ForeignKey
from models.base import Base


class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, ForeignKey("mobile_lines.id"), nullable=False)

    voice_minutes_used = Column(Integer, nullable=False, default=0)
    sms_used = Column(Integer, nullable=False, default=0)
    data_used_gb = Column(DECIMAL(10, 2), nullable=False, default=0)

    usage_period = Column(String, nullable=False)
