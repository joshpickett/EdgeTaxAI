from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.schema import Table
import enum
from api.config.database import Base


class DocumentType(enum.Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    TAX_DOCUMENT = "tax_document"
    OTHER = "other"


class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    VERIFIED = "verified"


document_shares = Table(
    "document_shares",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
    Column("shared_with_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column("permissions", String(50), default="read", nullable=False),  # read, write, admin
)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(DocumentType), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=True)
    size = Column(Integer, nullable=True)  # in bytes
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    metadata = Column(String, nullable=True)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    user = relationship("Users", back_populates="documents")
    shared_with = relationship(
        "Users", secondary=document_shares, backref="shared_documents"
    )

    current_version_id = Column(
        Integer, ForeignKey("document_versions.id"), nullable=True
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    changes = Column(String, nullable=True)  # JSON string describing changes
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    document = relationship("Document", backref="versions")
    user = relationship("Users", foreign_keys=[created_by])