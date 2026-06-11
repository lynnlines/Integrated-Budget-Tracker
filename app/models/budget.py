import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    period = Column(String(length=16), nullable=False, default="monthly")
    total_amount_cents = Column(BigInteger, nullable=False)
    active = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    items = relationship("BudgetItem", back_populates="budget", cascade="all, delete-orphan")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    budget_id = Column(String(length=36), ForeignKey("budgets.id"), nullable=False)
    category_id = Column(String(length=36), ForeignKey("categories.id"), nullable=False)
    amount_cents = Column(BigInteger, nullable=False)
    budget = relationship("Budget", back_populates="items")
