import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from app.db.base import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    parent_id = Column(String(length=36), ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
