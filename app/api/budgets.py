from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.schemas.budget import BudgetCreate, BudgetOut
from app.repositories.budget_repo import create_budget, list_budgets
from app.api.deps import get_db

router = APIRouter()


@router.post("/", response_model=BudgetOut)
def create_budget_endpoint(budget_in: BudgetCreate, db: Session = Depends(get_db)):
    budget = create_budget(db, budget_in.dict())
    return budget


@router.get("/", response_model=List[BudgetOut])
def get_budgets(db: Session = Depends(get_db)):
    return list_budgets(db)
