import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.validation import Load
from backend.app.config import settings

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/download/{load_id}")
def download_validation_report(load_id: int, db: Session = Depends(get_db)):
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load or not load.report_path:
        raise HTTPException(status_code=404, detail="Validation report file not found")

    file_path = load.report_path
    if not os.path.exists(file_path):
        # Check in default report dir
        basename = os.path.basename(file_path)
        alt_path = os.path.join(settings.REPORT_DIR, basename)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"Report file on disk not found: {basename}")

    filename = os.path.basename(file_path)
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )

