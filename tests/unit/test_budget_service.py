from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.category import Category
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.services.budget import get_monthly_summary, get_category_summary


def create_test_session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def test_get_monthly_summary_calculates_spent_income_and_budget():
    db = create_test_session()
    category = Category(name="Dining")
    db.add(category)
    db.commit()
    db.refresh(category)

    budget = Budget(name="June Budget", period="monthly", total_amount_cents=100000, active=1)
    db.add(budget)
    db.commit()
    db.refresh(budget)

    tx1 = Transaction(
        account_id="acct-1",
        posted_at=datetime(2026, 6, 5),
        description="Restaurant",
        amount_cents=-2500,
        currency="USD",
        category_id=category.id,
    )
    tx2 = Transaction(
        account_id="acct-1",
        posted_at=datetime(2026, 6, 10),
        description="Salary",
        amount_cents=500000,
        currency="USD",
    )
    db.add_all([tx1, tx2])
    db.commit()

    summary = get_monthly_summary(db, 2026, 6)

    assert summary["year"] == 2026
    assert summary["month"] == 6
    assert summary["total_spent_cents"] == -2500
    assert summary["total_income_cents"] == 500000
    assert summary["budget_total_cents"] == 100000
    assert summary["budget_used_cents"] == 2500
    assert summary["budget_variance_cents"] == 97500

    dining_row = next((row for row in summary["category_breakdown"] if row["category_name"] == "Dining"), None)
    assert dining_row is not None
    assert dining_row["amount_cents"] == -2500


def test_get_category_summary_returns_category_breakdown_for_date_range():
    db = create_test_session()
    category = Category(name="Utilities")
    db.add(category)
    db.commit()
    db.refresh(category)

    tx = Transaction(
        account_id="acct-1",
        posted_at=datetime(2026, 6, 15),
        description="Electric bill",
        amount_cents=-8000,
        currency="USD",
        category_id=category.id,
    )
    db.add(tx)
    db.commit()

    category_summary = get_category_summary(db, date(2026, 6, 1), date(2026, 6, 30))

    assert category_summary["start_date"] == date(2026, 6, 1)
    assert category_summary["end_date"] == date(2026, 6, 30)
    assert len(category_summary["categories"]) == 1
    assert category_summary["categories"][0]["category_name"] == "Utilities"
    assert category_summary["categories"][0]["amount_cents"] == -8000
