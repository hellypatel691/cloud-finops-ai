from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.upload_schema import UploadResponse
from app.services.upload_service import create_upload, get_uploads, get_upload

router = APIRouter(
    prefix="/organizations/{organization_id}/uploads",
    tags=["Uploads"],
)


@router.post("/", response_model=UploadResponse, status_code=201)
async def upload_csv(
    organization_id: int,
    file: UploadFile = File(...),
    project_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("text/csv", "application/vnd.ms-excel", "application/octet-stream"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are accepted.",
        )

    file_bytes = await file.read()

    try:
        return create_upload(
            db,
            organization_id,
            file_bytes,
            file.filename or "upload.csv",
            project_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[UploadResponse])
def read_all(
    organization_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_uploads(db, organization_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{upload_id}", response_model=UploadResponse)
def read_one(
    organization_id: int,
    upload_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_upload(db, organization_id, upload_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
