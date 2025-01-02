from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from api.config.database import Base
from datetime import datetime


class DocumentSignature(Base):
    __tablename__ = "document_signatures"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    signature = Column(LargeBinary, nullable=False)
    certificate_id = Column(String(100))
    signed_at = Column(DateTime, default=datetime.utcnow)
    signature_algorithm = Column(String(50))
    verification_status = Column(String(20))

    # Relationships
    document = relationship("Document", back_populates="signatures")


Document.signatures = relationship("DocumentSignature", back_populates="document")
