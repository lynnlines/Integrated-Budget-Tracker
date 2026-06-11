import csv
import io
import hashlib
from datetime import datetime
from typing import IO, Iterable, Dict, Any

from .bank_connector import BankConnector
import httpx


class GoogleSheetsConnector(BankConnector):
    def _find_col(self, fieldnames, keywords):
        for f in fieldnames:
            low = f.lower()
            for kw in keywords:
                if kw.lower() in low:
                    return f
        return None

    def _parse_amount(self, raw_amount: str) -> int | None:
        if raw_amount is None:
            return None
        text = str(raw_amount).replace(",", "").strip()
        if not text:
            return None
        text = text.replace("(", "-").replace(")", "")
        try:
            value = float(text)
        except ValueError:
            return None
        return int(round(value * 100))

    def import_transactions(self, file: IO, account_id: str = None) -> Iterable[Dict[str, Any]]:
        raw = file.read()
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="replace")
        else:
            text = str(raw)

        sio = io.StringIO(text)
        reader = csv.DictReader(sio)
        if not reader.fieldnames:
            return []

        fieldnames = reader.fieldnames
        col_date = self._find_col(fieldnames, ["date", "transaction date", "posted_at", "posted at"])
        col_desc = self._find_col(fieldnames, ["description", "merchant", "payee", "details"])
        col_amount = self._find_col(fieldnames, ["amount", "debit", "credit", "value"])
        col_external = self._find_col(fieldnames, ["external_id", "transaction id", "id", "reference"])
        col_currency = self._find_col(fieldnames, ["currency"])

        for row in reader:
            raw_date = row.get(col_date, "") if col_date else ""
            posted_at = None
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y"):
                try:
                    posted_at = datetime.strptime(raw_date.strip(), fmt)
                    break
                except Exception:
                    continue
            if not posted_at:
                continue

            amount_cents = self._parse_amount(row.get(col_amount))
            if amount_cents is None:
                continue

            desc = (row.get(col_desc) or "").strip()
            external_id = (row.get(col_external) or "").strip() or None
            if not external_id:
                h = hashlib.sha1()
                h.update(posted_at.isoformat().encode())
                h.update(str(amount_cents).encode())
                h.update(desc.encode())
                external_id = h.hexdigest()

            currency = (row.get(col_currency) or "USD").strip() or "USD"
            if account_id is None:
                account_id = row.get("account_id") or row.get("Account ID")

            yield {
                "account_id": account_id,
                "external_id": external_id,
                "posted_at": posted_at,
                "description": desc,
                "raw_payee": desc,
                "merchant": desc,
                "amount_cents": amount_cents,
                "currency": currency,
                "normalized": {
                    "source": "google_sheets",
                    "raw": row,
                },
            }

    @staticmethod
    def download_sheet(sheet_url: str) -> IO[bytes]:
        url = sheet_url.strip()
        if "docs.google.com/spreadsheets" in url and "export?format=csv" not in url:
            if "/edit" in url:
                url = url.split("/edit")[0] + "/export?format=csv"
            elif url.endswith("/"):
                url = url.rstrip("/") + "/export?format=csv"
            else:
                url = url + "/export?format=csv"

        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            return io.BytesIO(response.content)
