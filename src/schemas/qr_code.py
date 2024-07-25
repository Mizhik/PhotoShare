
from pydantic import BaseModel
from uuid import UUID


class QrSchema(BaseModel):
    photo_id: UUID
    
class QrUrl(BaseModel):
    qr_code_url: str