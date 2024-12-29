from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from api.config.database import Base

class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"))
    plaid_transaction_id = Column(String(255), unique=True, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(255), nullable=False)
    merchant_name = Column(String(255), nullable=True)
    categories = Column(ARRAY(String), nullable=True)
    pending = Column(Boolean, default=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    bank_account = relationship("BankAccounts", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index('idx_bank_transactions_account_id', bank_account_id),
        Index('idx_bank_transactions_date', date),
        Index('idx_bank_transactions_plaid_id', plaid_transaction_id, unique=True),
    )
