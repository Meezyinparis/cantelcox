from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from models.base import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    line_id = Column(Integer, nullable=False)
    order_status = Column(String, nullable=False, default="PENDING")
    idempotency_key = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
