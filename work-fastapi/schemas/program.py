from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional

class ProgramBase(BaseModel):
    contents: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None # 「emd_time」がタイポであれば修正済みです

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(ProgramBase):
    pass

class ProgramOut(ProgramBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True  # SQLAlchemy モデルと連携するために必要