from fastapi.testclient import TestClient
from app.main import app


def test_create_budget_endpoint_calls_repo(monkeypatch):
    client = TestClient(app)
    captured = {}

    def fake_create(db, data):
        captured["data"] = data
        return {
            "id": "budget-1",
            "name": data["name"],
            "period": data["period"],
            "total_amount_cents": data["total_amount_cents"],
            "active": True,
            "items": [],
        }

    monkeypatch.setattr("app.api.budgets.create_budget", fake_create)

    payload = {
        "name": "June Plan",
        "period": "monthly",
        "total_amount_cents": 90000,
        "active": True,
        "items": [],
    }
    response = client.post("/api/v1/budgets/", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "budget-1"
    assert captured["data"]["name"] == "June Plan"


def test_list_budgets_endpoint_returns_data(monkeypatch):
    client = TestClient(app)

    def fake_list(db):
        return [
            {
                "id": "budget-1",
                "name": "June Plan",
                "period": "monthly",
                "total_amount_cents": 90000,
                "active": True,
                "items": [],
            }
        ]

    monkeypatch.setattr("app.api.budgets.list_budgets", fake_list)
    response = client.get("/api/v1/budgets/")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "June Plan"


def test_monthly_summary_endpoint_returns_expected_shape(monkeypatch):
    client = TestClient(app)

    def fake_summary(db, year, month, account_id=None):
        return {
            "year": year,
            "month": month,
            "total_spent_cents": -10000,
            "total_income_cents": 50000,
            "category_breakdown": [],
            "budget_total_cents": 100000,
            "budget_used_cents": 10000,
            "budget_variance_cents": 90000,
        }

    monkeypatch.setattr("app.api.summary.get_monthly_summary", fake_summary)
    response = client.get("/api/v1/summary/monthly?year=2026&month=6")

    assert response.status_code == 200
    assert response.json()["year"] == 2026
    assert response.json()["month"] == 6


def test_category_summary_endpoint_returns_expected_shape(monkeypatch):
    client = TestClient(app)

    def fake_category_summary(db, start_date, end_date):
        return {
            "start_date": "2026-06-01",
            "end_date": "2026-06-30",
            "categories": [],
        }

    monkeypatch.setattr("app.api.summary.get_category_summary", fake_category_summary)
    response = client.get("/api/v1/summary/categories?start_date=2026-06-01&end_date=2026-06-30")

    assert response.status_code == 200
    assert response.json()["start_date"] == "2026-06-01"
    assert response.json()["end_date"] == "2026-06-30"
