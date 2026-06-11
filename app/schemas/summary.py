from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class CategorySummaryItem(BaseModel):
    category_id: Optional[str]
    category_name: Optional[str]
    amount_cents: int


class MonthlySummaryResponse(BaseModel):
    year: int
    month: int
    total_spent_cents: int
    total_income_cents: int
    category_breakdown: List[CategorySummaryItem]
    budget_total_cents: Optional[int] = None
    budget_used_cents: Optional[int] = None
    budget_variance_cents: Optional[int] = None


class MonthlyHistoryItem(BaseModel):
    year: int
    month: int
    total_spent_cents: int
    total_income_cents: int


class MonthlyHistoryResponse(BaseModel):
    history: List[MonthlyHistoryItem]


class CategorySummaryResponse(BaseModel):
    start_date: date
    end_date: date
    categories: List[CategorySummaryItem]
