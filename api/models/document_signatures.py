from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from api.config.database import Base
from datetime import datetime
from api.models.documents import Document  # Import the Document class


class DocumentSignature(Base):
    __tablename__ = "document_signatures"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    signature = Column(LargeBinary, nullable=False)
    certificate_id = Column(String(100), nullable=True)
    signed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    signature_algorithm = Column(String(50), nullable=True)
    verification_status = Column(String(20), nullable=True)

    # Relationships
    document = relationship("Document", back_populates="signatures")


Document.signatures = relationship("DocumentSignature", back_populates="document")