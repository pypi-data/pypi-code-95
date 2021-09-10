from src.models.BaseModel import BaseModel


class User(BaseModel):
    ID: str = None
    Code: str = None
    Frequency: str = None
    DoorNum: str = None
    Fri: str = None
    Mon: str = None
    Name: str = None
    ReferenceID: str = None
    Schedule: str = None
    Sat: str = None
    Sun: str = None
    Tags: str = None
    Thur: str = None
    TimeEnd: str = None
    TimeStart: str = None
    Tue: str = None
    Wed: str = None

    def __init__(self):
        super(User, self).__init__()

    def get_prefix(self) -> str:
        return ""
