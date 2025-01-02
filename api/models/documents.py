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
    Column("document_id", Integer, ForeignKey("documents.id", ondelete="CASCADE")),
    Column("shared_with_id", Integer, ForeignKey("users.id", ondelete="CASCADE")),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
    Column("permissions", String(50), default="read"),  # read, write, admin
)


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    type = Column(SQLEnum(DocumentType))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    mime_type = Column(String(100))
    size = Column(Integer)  # in bytes
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    metadata = Column(String)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("Users", back_populates="documents")
    shared_with = relationship(
        "Users", secondary=document_shares, backref="shared_documents"
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)
    changes = Column(String)  # JSON string describing changes
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", backref="versions")
    user = relationship("Users", foreign_keys=[created_by])


Document.current_version_id = Column(
    Integer, ForeignKey("document_versions.id"), nullable=True
)
