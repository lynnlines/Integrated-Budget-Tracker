import uuid
from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(length=36), ForeignKey("accounts.id"), nullable=False)
    external_id = Column(String, nullable=True, index=True)
    posted_at = Column(DateTime(timezone=True), nullable=False)
    description = Column(String, nullable=True)
    raw_payee = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    amount_cents = Column(BigInteger, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    category_id = Column(String(length=36), nullable=True)
    normalized = Column(JSON, nullable=True)
    import_batch_id = Column(String(length=36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
