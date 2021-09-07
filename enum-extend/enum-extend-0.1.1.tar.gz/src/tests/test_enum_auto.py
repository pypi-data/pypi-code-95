# coding: utf-8
'''Test AutoEnum'''
import pytest
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    pytest.main([__file__])
from enum_extend import AutoEnum
import inspect

# region Enums
class EnumAuto01(AutoEnum):
    FIRST = 'First value'
    SECOND = 'Second value'
    THIRD = 'Third value'
    FOURTH = 'Fourth value'


class EnumAuto02(AutoEnum):
    NONE = (0, 'None Value equal to 0')
    FIRST = 'The first of many'
    SECOND = 'This is a second as in number'
    THIRD = ''
    FOURTH = 'This is the fourth'


class EnumAuto03(AutoEnum):
    FIRST = (-100, 'First value')
    SECOND = 'Second value'
    THIRD = (30, 'Third value')
    FOURTH = 'Fourth value'


class EnumAuto04(AutoEnum):
    FIRST = """
    First value.
    
    This value is the first of the enum and is
        expected of having value of 1
    """
    SECOND = """Second value.
    
    This value is the second of the enum and is
        expected of having value of 2
    """
    THIRD = """
            Third value.
    
            This value is the third of the enum and is
                expected of having value of 3"""
    FOURTH = """Fourth value.
    
        This value is the fourth of the enum and is
            expected of having value of 4
        """


class MyAutoEnum(AutoEnum):
    FIRST = ()
    SECOND = ()
    THIRD = ()
    FOURTH = ()


class OnlyAutoEnum(AutoEnum):
    NEG = -999
    LESS_NEG = ()
    NONE = 0
    FIRST = ()
    SECOND = ()
    TEN = 10
    TEN_PLUS = ()
    TWENTY = 20
    TWENTY_PLUS = ()


class OthAutoEnum(AutoEnum):
    NONE = (0, 'Represents that no value is set yet')
    FIRST = 'First value'
    SECOND = 'Second value'
    TEN = (10, 'Represents 10')
    TEN_PLUS = 'Represents above 10'
    TWENTY = (20, 'Represents 20')
    TWENTY_PLUS = 'Represents above 20'

# endregion Enums

# region Test
def test_01_equal():
    assert EnumAuto01.FIRST == 1
    assert EnumAuto01.SECOND.value == 2
    assert EnumAuto01.THIRD == 3
    assert EnumAuto01.FOURTH == 4


def test_01_less_than():
    assert EnumAuto01.FIRST < EnumAuto01.SECOND
    assert EnumAuto01.SECOND < EnumAuto01.THIRD
    assert EnumAuto01.SECOND < 3
    assert EnumAuto01.SECOND < "THIRD"
    assert EnumAuto01.THIRD < EnumAuto01.FOURTH


def test_01_less_than_or_equal():
    assert EnumAuto01.FIRST <= EnumAuto01.FIRST
    assert EnumAuto01.FIRST <= "FIRST"
    assert EnumAuto01.FIRST <= EnumAuto01.SECOND
    assert EnumAuto01.SECOND <= EnumAuto01.THIRD
    assert EnumAuto01.SECOND <= 3
    assert EnumAuto01.SECOND <= "THIRD"
    assert EnumAuto01.THIRD <= EnumAuto01.FOURTH


def test_01_greater_than():
    assert EnumAuto01.SECOND > EnumAuto01.FIRST
    assert EnumAuto01.THIRD > EnumAuto01.SECOND
    assert EnumAuto01.THIRD > 2
    assert EnumAuto01.FOURTH > EnumAuto01.THIRD
    assert EnumAuto01.FOURTH > "THIRD"


def test_01_greater_than_or_equal():
    assert EnumAuto01.FIRST >= EnumAuto01.FIRST
    assert EnumAuto01.SECOND >= EnumAuto01.FIRST
    assert EnumAuto01.THIRD >= EnumAuto01.SECOND
    assert EnumAuto01.THIRD >= EnumAuto01.THIRD
    assert EnumAuto01.THIRD >= 2
    assert EnumAuto01.THIRD >= 3
    assert EnumAuto01.FOURTH >= EnumAuto01.THIRD
    assert EnumAuto01.FOURTH >= "FOURTH"


def test_01_add():
    assert EnumAuto01.FIRST + EnumAuto01.FIRST == EnumAuto01.SECOND
    assert EnumAuto01.SECOND + EnumAuto01.FIRST == EnumAuto01.THIRD
    assert EnumAuto01.FIRST + EnumAuto01.THIRD == EnumAuto01.FOURTH
    assert EnumAuto01.FIRST + 3 == EnumAuto01.FOURTH
    assert EnumAuto01.FIRST + "THIRD" == EnumAuto01.FOURTH


def test_01_sub():
    assert EnumAuto01.SECOND - EnumAuto01.FIRST == EnumAuto01.FIRST
    assert EnumAuto01.THIRD - EnumAuto01.FIRST == EnumAuto01.SECOND
    assert EnumAuto01.THIRD - EnumAuto01.SECOND == EnumAuto01.FIRST
    assert EnumAuto01.THIRD - 2 == EnumAuto01.FIRST
    assert EnumAuto01.THIRD - "SECOND" == EnumAuto01.FIRST


def test_01_doc_str():
    assert EnumAuto01.FIRST.__doc__ == 'First value'
    assert inspect.getdoc(EnumAuto01.FIRST) == 'First value'
    assert EnumAuto01.SECOND.__doc__ == 'Second value'
    assert inspect.getdoc(EnumAuto01.SECOND) == 'Second value'
    assert EnumAuto01.THIRD.__doc__ == 'Third value'
    assert inspect.getdoc(EnumAuto01.THIRD) == 'Third value'
    assert EnumAuto01.FOURTH.__doc__ == 'Fourth value'
    assert inspect.getdoc(EnumAuto01.FOURTH) == 'Fourth value'


def test_02_equal():
    e_first = EnumAuto02.NONE
    e_second = EnumAuto02.NONE
    assert e_first == e_second
    assert e_first == 0
    assert EnumAuto02.FIRST == 1
    assert EnumAuto02.SECOND.value == 2
    assert EnumAuto02.THIRD == 3
    assert EnumAuto02.FOURTH == 4


def test_03_equal():
    assert EnumAuto03.FIRST == -100
    assert EnumAuto03.SECOND == -99
    assert EnumAuto03.THIRD == 30
    assert EnumAuto03.FOURTH == 31


def test_04_doc_str():
    doc_str = EnumAuto04.FIRST.__doc__
    expect_str = "First value.\n\nThis value is the first of the enum and is\n    expected of having value of 1"
    assert doc_str == expect_str
    assert inspect.getdoc(EnumAuto04.FIRST) == expect_str
    doc_str = EnumAuto04.SECOND.__doc__
    expect_str = "Second value.\n\nThis value is the second of the enum and is\n    expected of having value of 2"
    assert doc_str == expect_str
    assert inspect.getdoc(EnumAuto04.SECOND) == expect_str
    doc_str = EnumAuto04.THIRD.__doc__
    expect_str = "Third value.\n\nThis value is the third of the enum and is\n    expected of having value of 3"
    assert doc_str == expect_str
    assert inspect.getdoc(EnumAuto04.THIRD) == expect_str
    doc_str = EnumAuto04.FOURTH.__doc__
    expect_str = "Fourth value.\n\nThis value is the fourth of the enum and is\n    expected of having value of 4"
    assert doc_str == expect_str
    assert inspect.getdoc(EnumAuto04.FOURTH) == expect_str


def test_auto_number_error():
    '''
    Test raises value error when a second item is added with a value less than previous items
    '''
    with pytest.raises(ValueError):
        exec("""class EnumAutoError(AutoEnum):
                    FIRST = 'First value'
                    SECOND = (0, 'Second value')
                    """)

def test_incorrect_params_error():
    '''
    Test raises type error incorrect number of params are added
    '''
    with pytest.raises(TypeError):
        exec("""class EnumAutoError(AutoEnum):
                    FIRST = 'First value'
                    SECOND = (2, 'Second value', 0)
                    """)

def test_my_auto_enum():
    assert MyAutoEnum.FIRST.value == 1
    assert MyAutoEnum.SECOND.value == 2
    assert MyAutoEnum.THIRD.value == 3
    assert MyAutoEnum.FOURTH.value == 4


def test_only_auto_enum():
    assert OnlyAutoEnum.NEG.value == -999
    assert OnlyAutoEnum.LESS_NEG.value == -998
    assert OnlyAutoEnum.NONE.value == 0
    assert OnlyAutoEnum.FIRST.value == 1
    assert OnlyAutoEnum.SECOND.value == 2
    assert OnlyAutoEnum.TEN.value == 10
    assert OnlyAutoEnum.TEN_PLUS.value == 11
    assert OnlyAutoEnum.TWENTY.value == 20
    assert OnlyAutoEnum.TWENTY_PLUS.value == 21
    assert OnlyAutoEnum.TEN_PLUS > OnlyAutoEnum.TEN

def test_oth_auto_enum():
    assert OthAutoEnum.NONE.value == 0
    assert OthAutoEnum.SECOND.value == 2
    assert OthAutoEnum.TWENTY.value == 20
    assert OthAutoEnum.TEN_PLUS.value == 11
    assert OthAutoEnum.TEN_PLUS > OthAutoEnum.TEN
    assert OthAutoEnum.TWENTY.__doc__ == 'Represents 20'

# endregion Test
