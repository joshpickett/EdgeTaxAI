from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from api.config.database import Base

class ExpenseCategory(enum.Enum):
    Vehicle = "Vehicle"
    HomeOffice = "Home Office"
    Supplies = "Supplies"
    Marketing = "Marketing"
    Other = "Other"

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    category = Column(Enum(ExpenseCategory), nullable=False)
    description = Column(String)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="expenses")
