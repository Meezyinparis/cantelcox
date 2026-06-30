from sqlalchemy import Column, Integer, String
from models.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    status = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
