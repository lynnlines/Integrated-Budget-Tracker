from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.monthly_summary import MonthlySummary


def get_monthly_summary_record(db: Session, year: int, month: int, account_id: Optional[str] = None):
    query = select(MonthlySummary).where(
        MonthlySummary.year == year,
        MonthlySummary.month == month,
    )
    if account_id is not None:
        query = query.where(MonthlySummary.account_id == account_id)
    else:
        query = query.where(MonthlySummary.account_id.is_(None))
    return db.execute(query).scalar_one_or_none()


def upsert_monthly_summary(
    db: Session,
    year: int,
    month: int,
    total_spent_cents: int,
    total_income_cents: int,
    per_category: list[dict],
    account_id: Optional[str] = None,
):
    record = get_monthly_summary_record(db, year, month, account_id)
    if record is None:
        record = MonthlySummary(
            year=year,
            month=month,
            account_id=account_id,
            total_spent_cents=total_spent_cents,
            total_income_cents=total_income_cents,
            per_category=per_category,
        )
        db.add(record)
    else:
        record.total_spent_cents = total_spent_cents
        record.total_income_cents = total_income_cents
        record.per_category = per_category
    db.commit()
    db.refresh(record)
    return record
