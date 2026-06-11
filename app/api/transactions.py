from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.schemas.transaction import TransactionOut
from app.db import session as db_session
from app.connectors.chase import ChaseConnector
from app.repositories.transaction_repo import insert_transactions
from app.services.categorizer import RuleEngine
from app.api.deps import get_db

router = APIRouter()


@router.get("/", response_model=List[TransactionOut])
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # placeholder - return empty list until repositories are implemented
    return []


@router.post("/import")
async def import_transactions(account_id: str = Form(None), file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required.")

    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload a CSV export.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    import io
    fh = io.BytesIO(content)

    connector = ChaseConnector()
    parsed = list(connector.import_transactions(fh, account_id=account_id))
    engine = RuleEngine(db)
    for p in parsed:
        try:
            p["category_id"] = engine.categorize(p)
        except Exception:
            p["category_id"] = None
    if not parsed:
        raise HTTPException(status_code=400, detail="No transactions parsed from file")

    summary = insert_transactions(db, parsed)
    return {"source": "chase", "account_id": account_id, "rows": len(parsed), **summary}
