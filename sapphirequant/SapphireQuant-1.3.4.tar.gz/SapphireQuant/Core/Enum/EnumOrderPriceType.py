from enum import Enum, unique


@unique
class EnumOrderPriceType(Enum):
    市价 = '1'
    限价 = '2'
    最优价 = '3'
    最新价 = '4'
    最新价浮动上浮1个ticks = '5'
    最新价浮动上浮2个ticks = '6'
    最新价浮动上浮3个ticks = '7'
    卖一价 = '8'
    卖一价浮动上浮1个ticks = '9'
    卖一价浮动上浮2个ticks = 'A'
    卖一价浮动上浮3个ticks = 'B'
    买一价 = 'C'
    买一价浮动上浮1个ticks = 'D'
    买一价浮动上浮2个ticks = 'E'
    买一价浮动上浮3个ticks = 'F'
    五档价 = 'G'

