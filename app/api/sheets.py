import io
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.google_sheets import sync_google_sheets
from app.connectors.google_sheets import GoogleSheetsConnector

router = APIRouter()


def validate_google_sheet_url(sheet_url: str) -> str:
    parsed = urlparse(sheet_url.strip())
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Google Sheets URL must use http or https.")
    if parsed.netloc not in ("docs.google.com", "www.docs.google.com"):
        raise ValueError("Only Google Sheets URLs are supported.")
    if not parsed.path.startswith("/spreadsheets/"):
        raise ValueError("Invalid Google Sheets URL path.")
    return sheet_url.strip()


@router.post("/import")
async def import_google_sheets(
    account_id: str | None = Form(None),
    sheet_url: str | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    if not account_id:
        raise HTTPException(status_code=400, detail="account_id is required.")
    if sheet_url and file:
        raise HTTPException(status_code=400, detail="Provide either sheet_url or file, not both.")
    if not sheet_url and file is None:
        raise HTTPException(status_code=400, detail="Provide either sheet_url or file.")

    if sheet_url:
        try:
            validated_url = validate_google_sheet_url(sheet_url)
            sheet_file = GoogleSheetsConnector.download_sheet(validated_url)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Unable to download sheet: {exc}")
    else:
        if file.content_type not in ("text/csv", "application/vnd.ms-excel", "text/plain"):
            raise HTTPException(status_code=400, detail="Uploaded file must be a CSV export.")
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        sheet_file = io.BytesIO(content)

    summary = sync_google_sheets(db, sheet_file, account_id=account_id)
    return {"source": "google_sheets", "rows": summary["inserted"], "duplicates": summary["duplicates"]}
