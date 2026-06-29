from sqlalchemy import Column, Integer, DECIMAL, String, ForeignKey
from models.base import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, nullable=False)
    line_id = Column(Integer, ForeignKey("mobile_lines.id"), nullable=False)
    billing_cycle = Column(String, nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    invoice_status = Column(String, nullable=False, default="UNPAID")