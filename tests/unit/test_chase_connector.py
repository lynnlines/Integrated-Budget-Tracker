import io
from app.connectors.chase import ChaseConnector


def test_parses_chase_csv():
    csv = (
        "Posting Date,Description,Amount,Check or Slip #\n"
        "6/1/2026,STARBUCKS STORE 123,-4.25,\n"
        "6/2/2026,SHELL OIL,-45.67,\n"
    )
    fh = io.BytesIO(csv.encode("utf-8"))
    c = ChaseConnector()
    parsed = list(c.import_transactions(fh, account_id="acct-1"))
    assert len(parsed) == 2
    s = parsed[0]
    assert s["description"].upper().startswith("STARBUCKS")
    assert s["amount_cents"] == -425
    assert "external_id" in s and s["external_id"]
