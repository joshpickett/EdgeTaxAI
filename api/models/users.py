from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import enum
from api.config.database import Base

class UserRole(enum.Enum):
    Admin = "Admin"
    User = "User"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.User)
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime(timezone=True), nullable=True)
    biometric_data = Column(String, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    personal_info = relationship("PersonalInformation", back_populates="user", 
                               uselist=False, cascade="all, delete-orphan")
    income = relationship("Income", back_populates="user")
    expenses = relationship("Expenses", back_populates="user")
    tax_payments = relationship("TaxPayments", back_populates="user")
    bank_accounts = relationship("BankAccounts", back_populates="user", cascade="all, delete-orphan")
    gig_platforms = relationship("GigPlatform", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    deductions = relationship("Deductions", back_populates="user")
    tax_forms = relationship("TaxForms", back_populates="user")
