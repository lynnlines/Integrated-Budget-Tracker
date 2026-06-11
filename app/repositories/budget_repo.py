from typing import List
from sqlalchemy.orm import Session
from app.models.budget import Budget, BudgetItem


def create_budget(db: Session, budget_data: dict):
    budget = Budget(
        name=budget_data["name"],
        period=budget_data.get("period", "monthly"),
        total_amount_cents=budget_data["total_amount_cents"],
        active=1 if budget_data.get("active", True) else 0,
    )
    db.add(budget)
    db.flush()

    items = []
    for item in budget_data.get("items", []):
        bi = BudgetItem(
            budget_id=budget.id,
            category_id=item["category_id"],
            amount_cents=item["amount_cents"],
        )
        db.add(bi)
        items.append(bi)

    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session) -> List[Budget]:
    return db.query(Budget).all()
