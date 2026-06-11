"""Demo seeder: load `data/sample_transactions.csv` into the DB.

Usage:
    .venv\Scripts\python.exe -m app.db.seed_demo

This script is safe to run repeatedly and will not duplicate transactions.
"""
import os
import csv
from datetime import datetime
from pathlib import Path

# Import DB session and models inside `seed()` so we can set a sensible
# default DATABASE_URL if it's not configured; this avoids mismatches
# between alembic's DB file (sqlite:///./test.db) and the in-memory default.
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_transactions.csv"


def parse_row(row):
    return {
        "date": datetime.fromisoformat(row["date"]).date(),
        "payee": row.get("payee"),
        "amount_cents": int(float(row.get("amount", "0")) * 100),
        "currency": row.get("currency", "USD"),
        "account_name": row.get("account_name", "Demo Account"),
        "category": row.get("category") or None,
    }


def seed():
    # Ensure DATABASE_URL matches the file DB used by alembic when not set.
    if os.getenv("DATABASE_URL") is None:
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"

    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        # Create or reuse demo account
        account = db.query(Account).filter(Account.name == "Demo Account").first()
        if not account:
            account = Account(name="Demo Account")
            db.add(account)
            db.commit()
            db.refresh(account)

        # Ensure categories exist and build cache
        categories_cache = {}
        if DATA_PATH.exists():
            with open(DATA_PATH, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    cat_name = row.get("category")
                    if not cat_name:
                        continue
                    cat = db.query(Category).filter(Category.name == cat_name).first()
                    if not cat:
                        cat = Category(name=cat_name)
                        db.add(cat)
                        db.commit()
                        db.refresh(cat)
                    categories_cache[cat_name] = cat

        # Insert transactions (skip duplicates)
        if DATA_PATH.exists():
            with open(DATA_PATH, newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    parsed = parse_row(row)
                    exists = db.query(Transaction).filter(
                        Transaction.posted_at == parsed["date"],
                        Transaction.raw_payee == parsed["payee"],
                        Transaction.amount_cents == parsed["amount_cents"],
                    ).first()
                    if exists:
                        continue
                    tx = Transaction(
                        posted_at=parsed["date"],
                        raw_payee=parsed["payee"],
                        description=parsed.get("payee"),
                        amount_cents=parsed["amount_cents"],
                        currency=parsed["currency"],
                        account_id=account.id,
                    )
                    cat_name = parsed.get("category")
                    if cat_name and categories_cache.get(cat_name):
                        tx.category_id = categories_cache[cat_name].id
                    db.add(tx)
                db.commit()
            print("Demo seeding complete.")
        else:
            print("Demo CSV not found:", DATA_PATH)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
