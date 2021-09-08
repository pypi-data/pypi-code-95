
import enum


@enum.unique
class EnumNetworkType(enum.Enum):
    un_know = -1,
    telecom = 0,
    unicom = 1
