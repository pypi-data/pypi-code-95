"""
@author  : MG
@Time    : 2021/7/21 9:06
@File    : symbol.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import logging
import re
from typing import Optional, Tuple

from vnpy_extra.constants import SYMBOL_SIZE_DIC, INSTRUMENT_RATE_DIC, INSTRUMENT_PRICE_TICK_DIC

pattern4 = re.compile(r"(?<=[a-zA-Z])\d{4}")
pattern2 = re.compile(r"(?<=[a-zA-Z])\d{2}")
PATTERN_INSTRUMENT_TYPE = re.compile(r'[a-zA-Z]+(?=\d{2,4})', re.IGNORECASE)
PATTERN_INSTRUMENT_TYPE_RESTRICT = re.compile(r'[a-zA-Z]+(?=\d{2,4}$)', re.IGNORECASE)
PATTERN_INSTRUMENT_TYPE_EXCHANGE_SPLIT = re.compile(r"(?<=[a-zA-Z])\d{3,4}\.", re.IGNORECASE)
PATTERN_PUT_OPTION = re.compile(r'[a-zA-Z]+-?\d+-?P-?\d+')
PATTERN_CALL_OPTION = re.compile(r'[a-zA-Z]+-?\d+-?C-?\d+')
PATTERN_SYMBOL_CALL_PUT_SPLIT = re.compile(r'(\w+-?\d+)-?([C|P])-?(\d+)')
PATTERN_OPTION_TYPE_EXCHANGE_SPLIT = re.compile(r"(?<=[a-zA-Z])\d{3,4}-?[C|P]-?\d+\.(?=[a-zA-Z]{3,4})", re.IGNORECASE)
PATTERN_INSTRUMENT_TYPE_OPTION = re.compile(r'[a-zA-Z]+(?=\d{3,4}-?[C|P]-?\d+)', re.IGNORECASE)
logger = logging.getLogger(__name__)


# PATTERN_SYMBOL_CALL_PUT_SPLIT.split('ru2110C12250.DCE') -> ['', 'ru2110', 'C', '12250', '.DCE']
# PATTERN_SYMBOL_CALL_PUT_SPLIT.split('ru2110.DCE') -> ['ru2110.DCE']


def get_contract_month(contract: str):
    """
    根据合约名称获取合约的月份，包括月份连续合约的格式，例如。RB01.SHF
    """
    match = pattern4.search(contract)
    if match is not None:
        return int(match.group()[2:])
    match = pattern2.search(contract)
    if match is not None:
        return int(match.group())
    raise ValueError(f'合约 {contract} 格式无效')


def get_instrument_type(symbol, pattern=None, error_log=True) -> Optional[str]:
    """匹配 instrument_type"""
    if pattern is None:
        pattern = PATTERN_INSTRUMENT_TYPE

    match = pattern.search(symbol)
    if match:
        instrument_type = match.group()
    else:
        instrument_type = None
        if error_log:
            logger.error("当前合约 %s 无法判断品种 pattern=%s", symbol, pattern.pattern)

    return instrument_type.upper() if instrument_type is not None else None


def _test_get_instrument_type():
    ret = get_instrument_type('rb9999.shfe')
    assert ret == 'RB'
    ret = get_instrument_type('rb9999')
    assert ret == 'RB'
    ret = get_instrument_type('MA2110-P-1975.DCE', pattern=PATTERN_INSTRUMENT_TYPE_OPTION)
    assert ret == 'MA'
    ret = get_instrument_type('MA2110-P-1975', pattern=PATTERN_INSTRUMENT_TYPE_OPTION)
    assert ret == 'MA'


def get_instrument_type_and_exchange(vt_symbol, pattern=None) -> Tuple[Optional[str], Optional[str]]:
    if pattern is None:
        pattern = PATTERN_INSTRUMENT_TYPE_EXCHANGE_SPLIT
    ret = tuple(pattern.split(vt_symbol))
    if len(ret) != 2:
        ret = None, None
    return ret


def _test_get_instrument_type_and_exchange():
    ret = get_instrument_type_and_exchange('rb9999.shfe')
    assert ret == ('rb', 'shfe')
    ret = get_instrument_type_and_exchange('MA2110-P-1975.DCE', PATTERN_OPTION_TYPE_EXCHANGE_SPLIT)
    assert ret == ('MA', 'DCE')
    try:
        ret = get_instrument_type_and_exchange('9999.shfe')
        assert False, '不应该被识别'
    except AssertionError:
        pass


def get_main_contract(vt_symbol) -> str:
    """将某一个合约品种变为主力连续合约"""
    new_vt_symbol = get_instrument_type(vt_symbol) + '9999.' + vt_symbol.split('.')[-1]
    return new_vt_symbol


def get_vt_symbol_multiplier(vt_symbol: str) -> float:
    return SYMBOL_SIZE_DIC[get_instrument_type(vt_symbol)]


def _test_get_vt_symbol_multiplier():
    assert get_vt_symbol_multiplier('rb2101.SHFE') == 10


def get_vt_symbol_rate(vt_symbol: str) -> float:
    return INSTRUMENT_RATE_DIC[get_instrument_type(vt_symbol)]


def _test_get_vt_symbol_rate():
    assert get_vt_symbol_rate('rb2101.SHFE') == 1.637651848101266e-4
    assert get_vt_symbol_rate('zz2101.SHFE') == 6e-05


def get_price_tick(vt_symbol: str) -> float:
    return INSTRUMENT_PRICE_TICK_DIC[get_instrument_type(vt_symbol)]


def _test_get_price_tick():
    assert get_price_tick('t2101.SHFE') == 0.005
    assert get_price_tick('zz2101.SHFE') == 1


if __name__ == "__main__":
    # _test_get_vt_symbol_multiplier()
    # _test_get_instrument_type()
    # _test_get_instrument_type_and_exchange()
    # _test_get_vt_symbol_multiplier()
    _test_get_price_tick()
