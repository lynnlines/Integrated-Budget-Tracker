import uuid
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    pattern = Column(String, nullable=False)
    match_type = Column(String, nullable=False, default="substring")  # substring|regex
    category_id = Column(String(length=36), ForeignKey("categories.id"), nullable=False)
    priority = Column(Integer, nullable=False, default=100)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
