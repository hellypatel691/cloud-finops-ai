from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.upload import UploadStatus


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    status: UploadStatus
    row_count: int | None
    error_message: str | None
    created_at: datetime
    organization_id: int
    project_id: int | None
