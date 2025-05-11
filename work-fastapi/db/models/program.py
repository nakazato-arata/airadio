from sqlalchemy import Column, Integer, String, Date, Time, DateTime
from db.database import Base
from datetime import datetime
from zoneinfo import ZoneInfo

class Program(Base):
    __tablename__ = "programs"
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(1000), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time) 
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())