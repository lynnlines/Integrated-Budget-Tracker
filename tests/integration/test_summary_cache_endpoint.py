from types import SimpleNamespace
from fastapi.testclient import TestClient
from app.main import app


def test_cached_monthly_returns_existing_record(monkeypatch):
    client = TestClient(app)

    fake_record = SimpleNamespace(
        year=2026,
        month=6,
        total_spent_cents=-1200,
        total_income_cents=0,
        per_category=[{"category_id": "c1", "category_name": "Dining", "amount_cents": -1200}],
    )

    def fake_get_monthly_summary_record(db, year, month, account_id=None):
        return fake_record

    def fake_get_monthly_summary(db, year, month, account_id=None):
        return {"budget_total_cents": 50000, "budget_used_cents": 1200, "budget_variance_cents": 48800}

    monkeypatch.setattr("app.api.summary.get_monthly_summary_record", fake_get_monthly_summary_record)
    monkeypatch.setattr("app.api.summary.get_monthly_summary", fake_get_monthly_summary)

    resp = client.get("/api/v1/summary/cache/monthly?year=2026&month=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["year"] == 2026
    assert data["month"] == 6
    assert data["total_spent_cents"] == -1200
    assert data["category_breakdown"][0]["category_name"] == "Dining"
    assert data["budget_total_cents"] == 50000


def test_cached_monthly_generates_when_missing(monkeypatch):
    client = TestClient(app)

    fake_record = SimpleNamespace(
        year=2026,
        month=6,
        total_spent_cents=-2500,
        total_income_cents=0,
        per_category=[{"category_id": "c1", "category_name": "Dining", "amount_cents": -2500}],
    )

    def fake_get_monthly_summary_record(db, year, month, account_id=None):
        return None

    def fake_refresh_monthly_summary(db, year, month, account_id=None):
        return fake_record

    def fake_get_monthly_summary(db, year, month, account_id=None):
        return {"budget_total_cents": 30000, "budget_used_cents": 2500, "budget_variance_cents": 27500}

    monkeypatch.setattr("app.api.summary.get_monthly_summary_record", fake_get_monthly_summary_record)
    monkeypatch.setattr("app.api.summary.refresh_monthly_summary", fake_refresh_monthly_summary)
    monkeypatch.setattr("app.api.summary.get_monthly_summary", fake_get_monthly_summary)

    resp = client.get("/api/v1/summary/cache/monthly?year=2026&month=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_spent_cents"] == -2500
    assert data["budget_total_cents"] == 30000


def test_dashboard_page_returns_html():
    client = TestClient(app)

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert "Budget Tracker Dashboard" in resp.text
    assert "chart.js" in resp.text.lower()
