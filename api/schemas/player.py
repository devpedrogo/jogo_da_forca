from pydantic import BaseModel


class PlayerCreate(BaseModel):
    name: str


class PlayerSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
