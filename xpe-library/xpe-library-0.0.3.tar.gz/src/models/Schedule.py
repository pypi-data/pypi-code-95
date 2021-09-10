from src.models.BaseModel import BaseModel

class Schedule(BaseModel):
    ID: str = None
    Name: str = None
    Type: str = None
    WeekDay: str = None
    StartDate: str = None
    EndDate: str = None
    StartTime: str = None
    EndTime: str = None