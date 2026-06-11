import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String(length=36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    institution = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
