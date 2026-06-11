from datetime import datetime, date, time
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.budget import Budget


def _normalize_date_range(start_date: date, end_date: date):
    start = datetime.combine(start_date, time.min)
    end = datetime.combine(end_date, time.max)
    return start, end


def _month_range(year: int, month: int):
    start = datetime(year, month, 1)
    end = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
    return start, end


def _apply_account_filter(query, account_id: Optional[str] = None):
    return query.filter(Transaction.account_id == account_id) if account_id else query


def _build_transaction_query(db: Session, start: datetime, end: datetime, account_id: Optional[str] = None):
    query = db.query(Transaction).filter(Transaction.posted_at >= start, Transaction.posted_at < end)
    return _apply_account_filter(query, account_id)


def _build_totals_query(db: Session, start: datetime, end: datetime, account_id: Optional[str] = None):
    totals = db.query(
        func.sum(case((Transaction.amount_cents < 0, Transaction.amount_cents), else_=0)).label("spent"),
        func.sum(case((Transaction.amount_cents > 0, Transaction.amount_cents), else_=0)).label("income"),
    ).select_from(Transaction)
    totals = totals.filter(Transaction.posted_at >= start, Transaction.posted_at < end)
    return _apply_account_filter(totals, account_id)


def _build_category_breakdown(db: Session, start: datetime, end: datetime, account_id: Optional[str] = None):
    query = (
        db.query(
            Transaction.category_id,
            Category.name.label("category_name"),
            func.sum(Transaction.amount_cents).label("amount_cents"),
        )
        .join(Category, Transaction.category_id == Category.id, isouter=True)
        .filter(
            Transaction.category_id.isnot(None),
            Transaction.posted_at >= start,
            Transaction.posted_at <= end,
        )
        .group_by(Transaction.category_id, Category.name)
    )
    return _apply_account_filter(query, account_id).all()


def get_monthly_summary(db: Session, year: int, month: int, account_id: Optional[str] = None):
    start, end = _month_range(year, month)
    totals = _build_totals_query(db, start, end, account_id).one()
    total_spent = int(totals.spent or 0)
    total_income = int(totals.income or 0)

    category_rows = _build_category_breakdown(db, start, end, account_id)
    category_breakdown = [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "amount_cents": int(row.amount_cents or 0),
        }
        for row in category_rows
    ]

    active_budget = db.query(Budget).filter(Budget.active == 1).order_by(Budget.created_at.desc()).first()
    budget_total = active_budget.total_amount_cents if active_budget else None
    budget_used = abs(total_spent) if total_spent < 0 else 0
    budget_variance = budget_total - budget_used if budget_total is not None else None

    return {
        "year": year,
        "month": month,
        "total_spent_cents": total_spent,
        "total_income_cents": total_income,
        "category_breakdown": category_breakdown,
        "budget_total_cents": budget_total,
        "budget_used_cents": budget_used,
        "budget_variance_cents": budget_variance,
    }


def get_monthly_history(db: Session, start_date: date, end_date: date, account_id: Optional[str] = None):
    start, end = _normalize_date_range(start_date, end_date)
    query = _apply_account_filter(db.query(Transaction), account_id)
    query = query.filter(Transaction.posted_at >= start, Transaction.posted_at <= end)

    history = {}
    for tx in query.all():
        year_month = (tx.posted_at.year, tx.posted_at.month)
        entry = history.setdefault(year_month, {"total_spent_cents": 0, "total_income_cents": 0})
        if tx.amount_cents < 0:
            entry["total_spent_cents"] += tx.amount_cents
        else:
            entry["total_income_cents"] += tx.amount_cents

    return [
        {
            "year": year,
            "month": month,
            "total_spent_cents": int(values["total_spent_cents"]),
            "total_income_cents": int(values["total_income_cents"]),
        }
        for (year, month), values in sorted(history.items())
    ]


def get_category_summary(db: Session, start_date: date, end_date: date):
    start, end = _normalize_date_range(start_date, end_date)
    category_rows = _build_category_breakdown(db, start, end)
    categories = [
        {
            "category_id": row.category_id,
            "category_name": row.category_name,
            "amount_cents": int(row.amount_cents or 0),
        }
        for row in category_rows
    ]
    return {
        "start_date": start_date,
        "end_date": end_date,
        "categories": categories,
    }
