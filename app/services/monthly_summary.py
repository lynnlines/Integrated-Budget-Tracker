from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.monthly_summary_repo import upsert_monthly_summary
from app.services.budget import get_monthly_summary


def refresh_monthly_summary(db: Session, year: int, month: int, account_id: Optional[str] = None):
    summary = get_monthly_summary(db, year, month, account_id)
    record = upsert_monthly_summary(
        db,
        year=year,
        month=month,
        total_spent_cents=summary["total_spent_cents"],
        total_income_cents=summary["total_income_cents"],
        per_category=summary["category_breakdown"],
        account_id=account_id,
    )
    return record


def refresh_current_month_summary(db: Session, account_id: Optional[str] = None):
    now = datetime.utcnow()
    return refresh_monthly_summary(db, now.year, now.month, account_id)
