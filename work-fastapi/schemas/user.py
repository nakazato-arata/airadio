from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str

class UserOut(UserCreate):
    id: int
    name: str

    class Config:
        orm_mode = True  # SQLAlchemy モデルと連携するために必要