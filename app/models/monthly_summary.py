import uuid
from sqlalchemy import Column, String, Integer, BigInteger, JSON
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base


class MonthlySummary(Base):
    __tablename__ = "monthly_summaries"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(length=36), nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_spent_cents = Column(BigInteger, nullable=False)
    total_income_cents = Column(BigInteger, nullable=False)
    per_category = Column(JSON, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
