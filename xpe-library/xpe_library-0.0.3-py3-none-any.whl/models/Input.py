from src.models.BaseModel import BaseModel


class Input(BaseModel):
    _PREFIX_PATH: str = "Config.DoorSetting.INPUT."
    InputEnable: str = None
    InputBEnable: str = None
    InputTrigger: str = None
    InputBTrigger: str = None
    InputRelay: str = None
    InputBRelay: str = None
    InputFtpEnable: str = None
    InputBFtpEnable: str = None
    InputHttpEnable: str = None
    InputSmtpEnable: str = None
    InputBSmtpEnable: str = None
    InputSipEnable: str = None
    InputBSipEnable: str = None
    InputABreakInIntrusion: str = None
    InputBBreakInIntrusion: str = None



