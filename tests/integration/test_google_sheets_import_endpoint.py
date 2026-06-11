import io
from fastapi.testclient import TestClient
from app.connectors.google_sheets import GoogleSheetsConnector
from app.main import app


def test_google_sheets_import_endpoint_calls_sync_service(monkeypatch):
    client = TestClient(app)

    def fake_sync_google_sheets(db, sheet_file, account_id=None):
        assert account_id == "acct-1"
        assert hasattr(sheet_file, "read")
        return {"inserted": 2, "duplicates": 0}

    monkeypatch.setattr("app.api.sheets.sync_google_sheets", fake_sync_google_sheets)

    csv = (
        "Date,Description,Amount,External ID\n"
        "2026-06-01,GOOGLE PLAY STORE,-9.99,tx-123\n"
        "2026-06-02,AMAZON.COM,-25.50,tx-124\n"
    )
    files = {"file": ("sheet.csv", csv, "text/csv")}
    data = {"account_id": "acct-1"}

    resp = client.post("/api/v1/sheets/import", files=files, data=data)

    assert resp.status_code == 200
    assert resp.json() == {"source": "google_sheets", "rows": 2, "duplicates": 0}


def test_google_sheets_import_endpoint_downloads_sheet_url(monkeypatch):
    client = TestClient(app)

    def fake_download_sheet(url):
        assert url == "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0"
        return io.BytesIO(
            b"Date,Description,Amount,External ID\n2026-06-01,GOOGLE PLAY STORE,-9.99,tx-123\n"
        )

    def fake_sync_google_sheets(db, sheet_file, account_id=None):
        assert account_id == "acct-1"
        assert sheet_file.read().startswith(b"Date,Description")
        return {"inserted": 1, "duplicates": 0}

    monkeypatch.setattr("app.api.sheets.GoogleSheetsConnector.download_sheet", staticmethod(fake_download_sheet))
    monkeypatch.setattr("app.api.sheets.sync_google_sheets", fake_sync_google_sheets)

    data = {"sheet_url": "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0", "account_id": "acct-1"}
    resp = client.post("/api/v1/sheets/import", data=data)

    assert resp.status_code == 200
    assert resp.json() == {"source": "google_sheets", "rows": 1, "duplicates": 0}
