from enum import Enum, unique


@unique
class EnumOrderType(Enum):
    normal = 48
    derive_from_quote = 49
    derivce_from_combination = 50
    combination = 51
    conditional_order = 52
    swap = 53
    derive_from_block_trade = 54
    derive_from_EFP_trade = 55
