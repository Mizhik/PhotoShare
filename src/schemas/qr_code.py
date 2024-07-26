
from pydantic import BaseModel
from uuid import UUID

class QrCreateResponse(BaseModel):
    id: UUID
    photo_id: UUID
    qr_code_url: str

class QrGetResponse(BaseModel):
    qr_code_url: str

