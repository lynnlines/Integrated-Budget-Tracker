from pydantic import BaseModel
from typing import Optional, List


class BudgetItemBase(BaseModel):
    category_id: str
    amount_cents: int


class BudgetItemCreate(BudgetItemBase):
    pass


class BudgetItemOut(BudgetItemBase):
    id: str

    class Config:
        from_attributes = True


class BudgetBase(BaseModel):
    name: str
    period: str = "monthly"
    total_amount_cents: int
    active: bool = True


class BudgetCreate(BudgetBase):
    items: List[BudgetItemCreate]


class BudgetOut(BudgetBase):
    id: str
    items: List[BudgetItemOut] = []

    class Config:
        from_attributes = True
