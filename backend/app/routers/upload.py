import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.engine.validator import DatasetValidator
from backend.app.config import settings
from backend.app.routers.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["Data Upload & Validation"])

@router.post("/validate")
async def upload_and_validate(
    template_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Client Dataset Upload and Automated Validation Workflow (Section III-D & Figure 16).
    1. Ingests uploaded Excel (.xlsx, .xls) or CSV file.
    2. Validates schema alignment with selected template.
    3. Deterministically executes all assigned validation rules.
    4. Generates Excel validation report with traceability.
    5. Dispatches real-time notification and logs audit trail.
    """
    if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an Excel (.xlsx, .xls) or CSV dataset."
        )

    # Save uploaded file to storage
    file_path = os.path.join(settings.UPLOAD_DIR, f"{int(current_user.id)}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload file: {str(e)}")

    try:
        result = DatasetValidator.process_and_validate(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
            file_path=file_path,
            filename=file.filename
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.get("/sample/{sample_key}")
def get_sample_file(sample_key: str):
    """
    Returns pre-generated research sample datasets for 1-click test runs.
    """
    samples = {
        "polizas_valid": ("Plantilla_polizas_valid.xlsx", "Plantilla_polizas"),
        "polizas_errors": ("Plantilla_polizas_with_errors.xlsx", "Plantilla_polizas"),
        "clientes_errors": ("Plantilla_clientes_with_errors.xlsx", "Plantilla_clientes"),
    }
    if sample_key not in samples:
        raise HTTPException(status_code=404, detail="Sample dataset not found")

    filename, template_name = samples[sample_key]
    sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", filename))
    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail=f"Sample file not found on disk: {sample_path}")

    from fastapi.responses import FileResponse
    return FileResponse(
        path=sample_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
        headers={"X-Template-Name": template_name}
    )


