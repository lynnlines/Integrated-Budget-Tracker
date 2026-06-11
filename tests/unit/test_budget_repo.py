from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.budget import BudgetItem
from app.models.category import Category
from app.repositories.budget_repo import create_budget, list_budgets


def create_test_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_create_budget_persists_budget_and_items():
    db = create_test_session()
    category = Category(name="Coffee")
    db.add(category)
    db.commit()
    db.refresh(category)

    budget_data = {
        "name": "June Budget",
        "period": "monthly",
        "total_amount_cents": 120000,
        "active": True,
        "items": [{"category_id": category.id, "amount_cents": 30000}],
    }

    budget = create_budget(db, budget_data)

    assert budget.id is not None
    assert budget.name == "June Budget"
    assert budget.total_amount_cents == 120000
    assert budget.active == 1
    assert len(budget.items) == 1
    assert budget.items[0].category_id == category.id
    assert budget.items[0].amount_cents == 30000


def test_list_budgets_returns_all_budgets():
    db = create_test_session()
    category = Category(name="Groceries")
    db.add(category)
    db.commit()
    db.refresh(category)

    budget_data = {
        "name": "Grocery Budget",
        "period": "monthly",
        "total_amount_cents": 50000,
        "active": True,
        "items": [{"category_id": category.id, "amount_cents": 50000}],
    }

    create_budget(db, budget_data)
    budgets = list_budgets(db)

    assert len(budgets) == 1
    assert budgets[0].name == "Grocery Budget"
