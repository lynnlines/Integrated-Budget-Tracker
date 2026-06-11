import io
from app.connectors.google_sheets import GoogleSheetsConnector


def test_parses_google_sheets_csv():
    csv = (
        "Date,Description,Amount,External ID,Currency\n"
        "2026-06-01,GOOGLE PLAY STORE,-9.99,tx-123,USD\n"
        "2026-06-02,AMAZON.COM,-25.50,tx-124,USD\n"
    )
    fh = io.BytesIO(csv.encode("utf-8"))
    connector = GoogleSheetsConnector()
    parsed = list(connector.import_transactions(fh, account_id="acct-1"))

    assert len(parsed) == 2
    first = parsed[0]
    assert first["description"] == "GOOGLE PLAY STORE"
    assert first["amount_cents"] == -999
    assert first["currency"] == "USD"
    assert first["account_id"] == "acct-1"
    assert first["external_id"] == "tx-123"


def test_download_sheet_converts_google_spreadsheet_url(monkeypatch):
    class FakeResponse:
        def __init__(self, content):
            self.content = content

        def raise_for_status(self):
            return None

    def fake_get(self, url):
        assert url.endswith("/export?format=csv")
        return FakeResponse(b"Date,Description,Amount,External ID\n")

    monkeypatch.setattr("app.connectors.google_sheets.httpx.Client.get", fake_get)

    result = GoogleSheetsConnector.download_sheet(
        "https://docs.google.com/spreadsheets/d/abc123/edit#gid=0"
    )
    assert result.read() == b"Date,Description,Amount,External ID\n"
