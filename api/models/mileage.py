from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.config.database import Base

class Mileage(Base):
    __tablename__ = "mileage"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    distance = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    purpose = Column(String(500))
    expense_id = Column(Integer, ForeignKey("expenses.id", nullable=True))
    deduction_id = Column(Integer, ForeignKey("deductions.id", nullable=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("Users", back_populates="mileage_records")
    expense = relationship("Expenses", back_populates="mileage_record")
    deduction = relationship("Deductions", back_populates="mileage_record")

class RecurringTrip(Base):
    __tablename__ = "recurring_trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    frequency = Column(String(50), nullable=False)  # daily, weekly, monthly
    purpose = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("Users", back_populates="recurring_trips")
