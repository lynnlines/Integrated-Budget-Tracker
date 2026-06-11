from io import IOBase
from typing import IO, Optional
from sqlalchemy.orm import Session
from app.connectors.google_sheets import GoogleSheetsConnector
from app.repositories.transaction_repo import insert_transactions
from app.services.categorizer import RuleEngine


def sync_google_sheets(db: Session, sheet_file: IO, account_id: Optional[str] = None):
    connector = GoogleSheetsConnector()
    transactions = list(connector.import_transactions(sheet_file, account_id=account_id))
    engine = RuleEngine(db)
    for tx in transactions:
        try:
            tx["category_id"] = engine.categorize(tx)
        except Exception:
            tx["category_id"] = None
    return insert_transactions(db, transactions)
