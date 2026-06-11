from datetime import date
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.summary import MonthlySummaryResponse, CategorySummaryResponse, MonthlyHistoryResponse
from app.api.deps import get_db
from app.services.budget import get_monthly_summary, get_category_summary, get_monthly_history
from app.repositories.monthly_summary_repo import get_monthly_summary_record
from app.services.monthly_summary import refresh_monthly_summary

router = APIRouter()


@router.get("/monthly", response_model=MonthlySummaryResponse)
def get_monthly_summary_endpoint(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    account_id: str | None = None,
    db: Session = Depends(get_db),
):
    return get_monthly_summary(db, year, month, account_id)


@router.get("/categories", response_model=CategorySummaryResponse)
def get_category_summary_endpoint(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return get_category_summary(db, start_date, end_date)


@router.get("/cache/monthly", response_model=MonthlySummaryResponse)
def get_cached_monthly_summary(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    account_id: str | None = None,
    db: Session = Depends(get_db),
):
    # Try to fetch persisted monthly summary
    record = get_monthly_summary_record(db, year, month, account_id=account_id)
    if record is None:
        # Build and persist if missing
        try:
            record = refresh_monthly_summary(db, year, month, account_id=account_id)
        except Exception as exc:  # pragma: no cover - defensive
            raise HTTPException(status_code=500, detail=f"Unable to generate monthly summary: {exc}")

    # Get budget fields from live calculation
    live = get_monthly_summary(db, year, month, account_id)

    return {
        "year": record.year,
        "month": record.month,
        "total_spent_cents": int(record.total_spent_cents),
        "total_income_cents": int(record.total_income_cents),
        "category_breakdown": record.per_category or [],
        "budget_total_cents": live.get("budget_total_cents"),
        "budget_used_cents": live.get("budget_used_cents"),
        "budget_variance_cents": live.get("budget_variance_cents"),
    }


@router.get("/history", response_model=MonthlyHistoryResponse)
def get_monthly_history_endpoint(
    start_date: date = Query(...),
    end_date: date = Query(...),
    account_id: str | None = None,
    db: Session = Depends(get_db),
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    return {"history": get_monthly_history(db, start_date, end_date, account_id)}
