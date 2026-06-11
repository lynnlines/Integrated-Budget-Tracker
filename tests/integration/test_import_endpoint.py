import io
from fastapi.testclient import TestClient
from app.main import app


def test_import_endpoint_parses_and_calls_repo(monkeypatch):
    client = TestClient(app)

    # fake insert_transactions to capture payload
    captured = {}

    def fake_insert(db, txs):
        captured["txs"] = list(txs)
        return {"inserted": len(captured["txs"]), "duplicates": 0}

    # fake RuleEngine to categorize STARBUCKS -> coffee
    class FakeRE:
        def __init__(self, db):
            pass

        def categorize(self, tx):
            desc = (tx.get("description") or "").upper()
            if "STARBUCKS" in desc:
                return "coffee"
            return None

    monkeypatch.setattr("app.api.transactions.insert_transactions", fake_insert)
    monkeypatch.setattr("app.api.transactions.RuleEngine", FakeRE)

    csv = (
        "Posting Date,Description,Amount,Check or Slip #\n"
        "6/1/2026,STARBUCKS STORE 123,-4.25,\n"
        "6/2/2026,SHELL OIL,-45.67,\n"
    )

    files = {"file": ("sample.csv", csv, "text/csv")}
    data = {"account_id": "acct-1"}
    resp = client.post("/api/v1/transactions/import", files=files, data=data)
    assert resp.status_code == 200
    j = resp.json()
    assert j["rows"] == 2
    assert j["inserted"] == 2
    # verify captured txs have category assigned for STARBUCKS
    assert any(t.get("category_id") == "coffee" for t in captured["txs"])
