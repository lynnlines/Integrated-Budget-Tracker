from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.monthly_summary import refresh_monthly_summary


def test_refresh_monthly_summary_creates_record():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as db:
        category = Category(name="Dining")
        db.add(category)
        db.commit()
        db.refresh(category)

        transaction = Transaction(
            account_id="acct-1",
            external_id="tx-100",
            posted_at=datetime(2026, 6, 15),
            description="Lunch",
            raw_payee="Lunch",
            merchant="Lunch",
            amount_cents=-1200,
            currency="USD",
            normalized={"source": "google_sheets", "raw": {}},
            category_id=category.id,
        )
        db.add(transaction)
        db.commit()

        summary = refresh_monthly_summary(db, 2026, 6)

        assert summary.year == 2026
        assert summary.month == 6
        assert summary.total_spent_cents == -1200
        assert summary.total_income_cents == 0
        assert summary.per_category == [
            {
                "category_id": category.id,
                "category_name": "Dining",
                "amount_cents": -1200,
            }
        ]


def test_refresh_monthly_summary_updates_existing_record():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(engine)

    with TestingSessionLocal() as db:
        category = Category(name="Dining")
        db.add(category)
        db.commit()
        db.refresh(category)

        transaction = Transaction(
            account_id="acct-2",
            external_id="tx-101",
            posted_at=datetime(2026, 6, 20),
            description="Dinner",
            raw_payee="Dinner",
            merchant="Dinner",
            amount_cents=-2500,
            currency="USD",
            normalized={"source": "google_sheets", "raw": {}},
            category_id=category.id,
        )
        db.add(transaction)
        db.commit()

        first_summary = refresh_monthly_summary(db, 2026, 6)
        second_summary = refresh_monthly_summary(db, 2026, 6)

        assert first_summary.id == second_summary.id
        assert second_summary.total_spent_cents == -2500
        assert second_summary.per_category[0]["category_name"] == "Dining"
