from fastapi import APIRouter
from app.api import transactions, budgets, summary, sheets

api_router = APIRouter()
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(summary.router, prefix="/summary", tags=["summary"])
api_router.include_router(sheets.router, prefix="/sheets", tags=["sheets"])
