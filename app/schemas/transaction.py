from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class TransactionBase(BaseModel):
    external_id: Optional[str]
    posted_at: datetime
    description: Optional[str]
    raw_payee: Optional[str]
    merchant: Optional[str]
    amount_cents: int
    currency: str = "USD"


class TransactionIn(TransactionBase):
    account_id: str


class TransactionOut(TransactionBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
