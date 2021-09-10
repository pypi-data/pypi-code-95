from src.models.BaseModel import BaseModel


class DTMF(BaseModel):
    __PREFIX_PATH = "Config.DoorSetting.DTMF."
    Enable: str = None
    Option: str = None
    Code1: str = None
    Code2: str = None
    MultiDTMFCodeA: str = None
    MultiDTMFCodeB: str = None

    def get_prefix(self) -> str:
        return self.__PREFIX_PATH
