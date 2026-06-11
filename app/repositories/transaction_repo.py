from typing import Iterable, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.transaction import Transaction


def transaction_exists(db: Session, external_id: str, posted_at, amount_cents: int, description: str) -> bool:
    if external_id:
        q = select(Transaction).where(Transaction.external_id == external_id)
        r = db.execute(q).scalar_one_or_none()
        if r:
            return True

    q2 = select(Transaction).where(
        Transaction.posted_at == posted_at,
        Transaction.amount_cents == amount_cents,
        Transaction.description == description,
    )
    r2 = db.execute(q2).scalar_one_or_none()
    return bool(r2)


def insert_transactions(db: Session, txs: Iterable[Dict[str, Any]]):
    inserted = 0
    duplicates = 0
    for t in txs:
        if transaction_exists(db, t.get("external_id"), t.get("posted_at"), t.get("amount_cents"), t.get("description")):
            duplicates += 1
            continue
        obj = Transaction(
            account_id=t.get("account_id"),
            external_id=t.get("external_id"),
            posted_at=t.get("posted_at"),
            description=t.get("description"),
            raw_payee=t.get("raw_payee"),
            merchant=t.get("merchant"),
            amount_cents=t.get("amount_cents"),
            currency=t.get("currency", "USD"),
            normalized=t.get("normalized"),
        )
        db.add(obj)
        inserted += 1

    db.commit()
    return {"inserted": inserted, "duplicates": duplicates}
