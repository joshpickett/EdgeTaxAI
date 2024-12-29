from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Numeric, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from api.config.database import Base
import enum

class UserRole(enum.Enum):
    Admin = "Admin"
    User = "User"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.User)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    personal_info = relationship("PersonalInformation", back_populates="user", uselist=False)
    income = relationship("Income", back_populates="user")
    expenses = relationship("Expenses", back_populates="user")
    tax_payments = relationship("TaxPayments", back_populates="user")

class PersonalInformation(Base):
    __tablename__ = "personal_information"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(15))
    ssn = Column(String(11), unique=True, nullable=False)
    dob = Column(Date, nullable=False)
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(50), nullable=False)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="personal_info")

class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    platform_name = Column(String(50))
    gross_income = Column(Numeric(10, 2))
    tips = Column(Numeric(10, 2))
    platform_fees = Column(Numeric(10, 2))
    mileage = Column(Numeric(10, 2))
    payer_name = Column(String(100))
    tin = Column(String(11))
    total_compensation = Column(Numeric(10, 2))
    employer_name = Column(String(100))
    ein = Column(String(11))
    wages = Column(Numeric(10, 2))
    federal_withholding = Column(Numeric(10, 2))
    state_withholding = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="income")

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    category = Column(String(50), nullable=False)
    description = Column(String)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="expenses")

class TaxPayments(Base):
    __tablename__ = "tax_payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    federal_payment = Column(Numeric(10, 2))
    state_payment = Column(Numeric(10, 2))
    date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("Users", back_populates="tax_payments")
