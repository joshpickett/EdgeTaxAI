from sqlalchemy import Column, Numeric, DateTime, Integer, ForeignKey, String, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
import enum
from api.config.database import Base

class ExpenseCategory(enum.Enum):
    SUPPLIES = "supplies"
    EQUIPMENT = "equipment"
    VEHICLE = "vehicle"
    INSURANCE = "insurance"
    OFFICE = "office"
    OTHER = "other"
    UNCATEGORIZED = "Uncategorized"

class Expenses(Base):
    __tablename__ = "expenses"

    # Primary key and foreign keys
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Core fields from database schema
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(SQLEnum(ExpenseCategory), default=ExpenseCategory.UNCATEGORIZED)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Additional fields from database schema
    confidence_score = Column(Float, default=0.0)
    tax_context = Column(String, default='personal')
    learning_feedback = Column(String, nullable=True)
    receipt = Column(String, nullable=True)

    # Additional fields from schema requirements
    receipt_url = Column(String(512), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    tax_year = Column(Integer)
    is_deductible = Column(Boolean, default=False)

    # Relationships
    user = relationship("Users", back_populates="expenses")
    document = relationship("Document", backref="expenses")

    def __repr__(self):
        return f"<Expense(id={self.id}, user_id={self.user_id}, amount={self.amount})>"