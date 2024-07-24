from pydantic import BaseModel


class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True
