from src.models.DTMF import DTMF
from src.models.BaseModel import BaseModel


class Relay(BaseModel):
    """
    Class to keep info about relay
    """
    __PREFIX_PATH = "Config.DoorSetting.RELAY."
    RelayAType: str = None
    RelayBType: str = None
    RelayCType: str = None
    RelayADelay: str = None
    RelayBDelay: str = None
    RelayCDelay: str = None
    TriggerDelayA: str = None
    TriggerDelayB: str = None
    TriggerDelayC: str = None
    RelayAName: str = None
    RelayBName: str = None
    RelayCName: str = None
    RelayOnWeb: str = None
    RelayOnWebUser: str = None
    RelayOnWebPwd: str = None
    InterLocking: str = None
    dtmf: DTMF = DTMF()

    def get_prefix(self) -> str:
        return self.__PREFIX_PATH
