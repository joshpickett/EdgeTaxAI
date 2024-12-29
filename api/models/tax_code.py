from sqlalchemy import Column, Integer, String, Text, DateTime, func
from api.config.database import Base

class TaxCode(Base):
    __tablename__ = "tax_code"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(10), nullable=False)
    section = Column(String(20), nullable=False)
    subsection = Column(String(20))
    description = Column(Text, nullable=False)
    full_text = Column(Text, nullable=False)
    keywords = Column(Text)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
