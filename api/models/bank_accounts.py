from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from api.utils.encryption_utils import EncryptionManager

encryption_manager = EncryptionManager()


class BankAccounts(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    account_number = Column(String(255), nullable=True)  # Encrypted
    routing_number = Column(String(255), nullable=True)  # Encrypted
    bank_name = Column(String(255), nullable=False)
    account_type = Column(Enum(BankAccountType), nullable=False)

    # Plaid specific fields
    plaid_account_id = Column(String(255), nullable=True)
    plaid_access_token = Column(String(255), nullable=True)
    plaid_item_id = Column(String(255), nullable=True)
    plaid_institution_id = Column(String(255), nullable=True)
    account_mask = Column(String(50), nullable=True)
    account_name = Column(String(255), nullable=True)
    official_name = Column(String(255), nullable=True)
    account_subtype = Column(String(50), nullable=True)

    # Security and audit fields
    last_sync = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("Users", back_populates="bank_accounts")
    transactions = relationship(
        "BankTransaction", back_populates="bank_account", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_bank_accounts_user_id", user_id),
        Index("idx_bank_accounts_plaid_account", plaid_account_id, unique=True),
    )
