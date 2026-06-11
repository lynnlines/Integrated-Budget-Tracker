import csv
import io
import hashlib
from datetime import datetime
from typing import Iterable, Dict, Any, IO

from .bank_connector import BankConnector


class ChaseConnector(BankConnector):
    def _find_col(self, fieldnames, keywords):
        for f in fieldnames:
            low = f.lower()
            for kw in keywords:
                if kw.lower() in low:
                    return f
        return None

    def import_transactions(self, file: IO, account_id: str = None) -> Iterable[Dict[str, Any]]:
        # read bytes and decode to string for csv parsing
        raw = file.read()
        if isinstance(raw, bytes):
            text = raw.decode("utf-8", errors="replace")
        else:
            text = str(raw)

        sio = io.StringIO(text)
        # let csv.DictReader sniff delimiter
        sample = sio.read(2048)
        sio.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.DictReader(sio, dialect=dialect)
        except Exception:
            reader = csv.DictReader(sio)

        # map columns
        fns = reader.fieldnames or []
        col_date = self._find_col(fns, ["posting date", "post date", "date"])
        col_desc = self._find_col(fns, ["description", "transaction information", "merchant"])
        col_amount = self._find_col(fns, ["amount"]) or self._find_col(fns, ["debit", "credit"])
        col_check = self._find_col(fns, ["check", "slip"]) or None

        for row in reader:
            # parse date
            raw_date = row.get(col_date, "") if col_date else ""
            posted_at = None
            for fmt in ("%m/%d/%Y", "%m/%d/%y"):
                try:
                    posted_at = datetime.strptime(raw_date.strip(), fmt)
                    break
                except Exception:
                    continue
            if not posted_at:
                # skip invalid rows
                continue

            desc = (row.get(col_desc) or "").strip()
            raw_payee = desc

            amt_str = (row.get(col_amount) or "").replace(",", "").strip()
            # Amounts may include parentheses or +/-, handle common formats
            amt_str = amt_str.replace("(", "-").replace(")", "")
            try:
                amount = float(amt_str)
            except Exception:
                # skip rows with invalid amount
                continue
            amount_cents = int(round(amount * 100))

            external_id = (row.get(col_check) or "") or None
            if not external_id:
                # fallback: deterministic hash of date+amount+desc
                h = hashlib.sha1()
                h.update(posted_at.isoformat().encode())
                h.update(str(amount_cents).encode())
                h.update(desc.encode())
                external_id = h.hexdigest()

            normalized = {
                "source": "chase",
                "raw": row,
            }

            yield {
                "account_id": account_id,
                "external_id": external_id,
                "posted_at": posted_at,
                "description": desc,
                "raw_payee": raw_payee,
                "merchant": desc,
                "amount_cents": amount_cents,
                "currency": "USD",
                "normalized": normalized,
            }
