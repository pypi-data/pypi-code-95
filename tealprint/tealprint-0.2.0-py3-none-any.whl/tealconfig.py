from .teallevel import TealLevel


class TealConfig:
    level: TealLevel = TealLevel.info
    indent_char = " "
    indent_by: int = 4
