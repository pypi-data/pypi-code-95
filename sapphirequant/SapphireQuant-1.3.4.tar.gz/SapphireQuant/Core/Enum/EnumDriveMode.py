from enum import Enum, unique


@unique
class EnumDriveMode(Enum):
    on_tick = 'T'
    on_bar = 'B'
    on_mix = 'm'
