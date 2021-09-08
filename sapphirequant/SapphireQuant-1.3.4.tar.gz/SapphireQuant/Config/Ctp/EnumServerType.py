
import enum


@enum.unique
class EnumServerType(enum.Enum):
    un_know = -1,
    trade = 0,
    quote = 1
