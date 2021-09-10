from src.models.BaseModel import BaseModel


class DialPlan(BaseModel):
    """
    Class to keep info about Dial plan
    """
    ID: str = None
    Prefix: str = None
    Replace: str = None
    Replace2: str = None
    Account1: str = None
    Account2: str = None
    TimeRinging: str = None
    GroupTime: str = None
