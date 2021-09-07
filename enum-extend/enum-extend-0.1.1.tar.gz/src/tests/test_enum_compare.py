# coding: utf-8
'''Test EnumComparable'''
from enum import Enum
import pytest
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.realpath('..'))
    pytest.main([__file__])
from enum_extend import EnumComparable, AutoEnum

class DummyClass(object):
    '''Dummy class'''

class NormalEnum(Enum):
    NONE = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4

class EnumTest(EnumComparable):
    NONE = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


@pytest.fixture(scope='module')
def enum_names():
    return ('NONE', 'FIRST', 'SECOND', 'THIRD', 'FOURTH')

def test_is():
    e_obj = EnumTest.NONE
    assert e_obj is EnumTest.NONE
    e_obj = EnumTest.FIRST
    assert e_obj is EnumTest.FIRST
    e_obj = EnumTest.SECOND
    assert e_obj is EnumTest.SECOND
    e_obj = EnumTest.THIRD
    assert e_obj is EnumTest.THIRD
    e_obj = EnumTest.FOURTH
    assert e_obj is EnumTest.FOURTH
    assert (EnumTest.FIRST is NormalEnum.FIRST) == False

def test_equal():
    e_first = EnumTest.NONE
    e_second = EnumTest.NONE
    assert e_first == e_second
    e_first = EnumTest.FIRST
    e_second = EnumTest.FIRST
    assert e_first == e_second
    e_first = EnumTest.THIRD
    e_second = EnumTest.THIRD
    assert e_first == e_second
    e_first = EnumTest.FOURTH
    e_second = EnumTest.FOURTH
    assert e_first == e_second
    assert (e_first == DummyClass()) == False
    assert EnumTest.FIRST == NormalEnum.FIRST


def test_equal_num():
    e_first = EnumTest.NONE
    e_second = 0
    assert e_first == e_second
    e_first = EnumTest.FIRST
    e_second = 1
    assert e_first == e_second
    e_first = EnumTest.THIRD
    e_second = 3
    assert e_first == e_second
    e_first = EnumTest.FOURTH
    e_second = 4
    assert e_first == e_second


def test_equal_str():
    e_first = EnumTest.NONE
    e_second = "NONE"
    assert e_first == e_second
    e_first = EnumTest.FIRST
    e_second = "FIRST"
    assert e_first == "EnumTest.FIRST"
    assert e_first == "  < EnumTest.FIRST ) "
    assert e_first == e_second
    e_first = EnumTest.THIRD
    e_second = "THIRD"
    assert e_first == e_second
    e_first = EnumTest.FOURTH
    e_second = "FOURTH"
    assert e_first == e_second


def test_not_equal():
    e_first = EnumTest.NONE
    e_second = EnumTest.FIRST
    assert e_first != e_second
    e_first = EnumTest.FIRST
    e_second = EnumTest.SECOND
    assert e_first != e_second
    assert e_first != "first"
    assert e_first != "FIRSt"
    assert e_first != "EnumTest.FIRSt"
    e_first = EnumTest.THIRD
    e_second = EnumTest.FOURTH
    assert e_first != e_second
    e_first = EnumTest.FIRST
    e_second = EnumTest.FOURTH
    assert e_first != e_second
    e_first = EnumTest.SECOND
    e_second = "FIRST"
    assert e_first != e_second
    e_first = EnumTest.NONE
    e_second = AutoEnum
    assert e_first != e_second
    assert e_first != DummyClass()


def test_less_than(enum_names):
    assert EnumTest.NONE < EnumTest.FIRST
    assert EnumTest.NONE < EnumTest.SECOND
    assert EnumTest.NONE < EnumTest.THIRD
    assert EnumTest.NONE < EnumTest.FOURTH
    assert EnumTest.FIRST < EnumTest.SECOND
    assert EnumTest.FIRST < EnumTest.THIRD
    assert EnumTest.FIRST < EnumTest.FOURTH
    assert EnumTest.SECOND < EnumTest.THIRD
    assert EnumTest.SECOND < EnumTest.FOURTH
    assert EnumTest.THIRD < EnumTest.FOURTH
    assert EnumTest.THIRD < 4
    assert EnumTest.FOURTH < 5
    assert (EnumTest.FOURTH < -1) == False
    for i in range(1, len(enum_names)):
        assert EnumTest.NONE < enum_names[i]
    for i in range(2, len(enum_names)):
        assert EnumTest.FIRST < enum_names[i]
    with pytest.raises(ValueError):
        EnumTest.NONE < 'nosense'
    with pytest.raises(TypeError):
        EnumTest.FIRST < DummyClass()


def test_less_than_or_equal(enum_names):
    assert EnumTest.NONE <= EnumTest.NONE
    assert EnumTest.NONE <= EnumTest.FIRST
    assert EnumTest.NONE <= EnumTest.SECOND
    assert EnumTest.NONE <= EnumTest.THIRD
    assert EnumTest.NONE <= EnumTest.FOURTH
    assert EnumTest.FIRST <= EnumTest.FIRST
    assert EnumTest.FIRST <= EnumTest.SECOND
    assert EnumTest.FIRST <= EnumTest.THIRD
    assert EnumTest.FIRST <= EnumTest.FOURTH
    assert EnumTest.SECOND <= EnumTest.SECOND
    assert EnumTest.SECOND <= EnumTest.THIRD
    assert EnumTest.SECOND <= EnumTest.FOURTH
    assert EnumTest.THIRD <= EnumTest.THIRD
    assert EnumTest.THIRD <= EnumTest.FOURTH
    assert EnumTest.FOURTH <= EnumTest.FOURTH
    assert EnumTest.THIRD <= 4
    assert EnumTest.FOURTH <= 4
    assert EnumTest.FOURTH <= 5
    assert EnumTest.FOURTH <= 333.444
    assert (EnumTest.FOURTH <= -99.0098) == False
    for name in enum_names:
        assert EnumTest.NONE <= name
    for name in enum_names:
        str_name = "EnumTest.{0}".format(name)
        assert EnumTest.NONE <= str_name
    for name in enum_names:
        str_name = "< EnumTest.{0} >".format(name)
        assert EnumTest.NONE <= str_name
    for name in enum_names:
        str_name = "dosen't . really matter.{0} .as long as name is split by '.' values".format(name)
        assert EnumTest.NONE <= str_name
    for i in range(1, len(enum_names)):
        assert EnumTest.FIRST <= enum_names[i]
    with pytest.raises(ValueError):
        EnumTest.NONE <= 'nosense'
    with pytest.raises(TypeError):
        EnumTest.FIRST <= DummyClass()


def test_greater_than(enum_names):
    assert EnumTest.FIRST > EnumTest.NONE
    assert EnumTest.SECOND > EnumTest.NONE
    assert EnumTest.SECOND > (EnumTest.NONE + EnumTest.FIRST)
    assert EnumTest.THIRD > EnumTest.NONE
    assert EnumTest.FOURTH > EnumTest.NONE
    assert EnumTest.SECOND > EnumTest.FIRST
    assert EnumTest.THIRD > EnumTest.FIRST
    assert EnumTest.FOURTH > EnumTest.FIRST
    assert EnumTest.THIRD > EnumTest.SECOND
    assert EnumTest.FOURTH > EnumTest.SECOND
    assert EnumTest.FOURTH > EnumTest.THIRD
    assert EnumTest.FOURTH > 0
    assert EnumTest.FOURTH > 1
    assert EnumTest.FOURTH > 2
    assert EnumTest.FOURTH > 3
    assert EnumTest.FOURTH > -1
    assert (EnumTest.FOURTH > 10) == False
    for i in range(len(enum_names)-2, -1, -1):
        assert EnumTest.FOURTH > enum_names[i]
    with pytest.raises(ValueError):
        EnumTest.NONE > 'nosense'
    with pytest.raises(TypeError):
        EnumTest.FIRST > DummyClass()


def test_greater_than_or_equal(enum_names):
    assert EnumTest.NONE >= EnumTest.NONE
    assert EnumTest.FIRST >= EnumTest.NONE
    assert EnumTest.SECOND >= EnumTest.NONE
    assert EnumTest.SECOND >= EnumTest.FIRST + EnumTest.FIRST
    assert EnumTest.THIRD >= EnumTest.NONE
    assert EnumTest.FOURTH >= EnumTest.NONE
    assert EnumTest.FIRST >= EnumTest.FIRST
    assert EnumTest.SECOND >= EnumTest.FIRST
    assert EnumTest.THIRD >= EnumTest.FIRST
    assert EnumTest.FOURTH >= EnumTest.FIRST
    assert EnumTest.SECOND >= EnumTest.SECOND
    assert EnumTest.THIRD >= EnumTest.SECOND
    assert EnumTest.FOURTH >= EnumTest.SECOND
    assert EnumTest.THIRD >= EnumTest.THIRD
    assert EnumTest.FOURTH >= EnumTest.THIRD
    assert EnumTest.FOURTH >= EnumTest.FOURTH
    assert EnumTest.FOURTH >= 0
    assert EnumTest.FOURTH >= 1
    assert EnumTest.FOURTH >= 2
    assert EnumTest.FOURTH >= 3
    assert EnumTest.FOURTH >= 4
    assert EnumTest.FOURTH >= -1
    assert EnumTest.FOURTH >= 2.1
    assert (EnumTest.FOURTH >= 22.999) == False
    for i in range(len(enum_names)-1, -1, -1):
        assert EnumTest.FOURTH >= enum_names[i]
    with pytest.raises(ValueError):
        EnumTest.NONE >= 'nosense'
    with pytest.raises(TypeError):
        EnumTest.FIRST >= DummyClass()


def test_add():
    e_obj = EnumTest.FIRST + EnumTest.SECOND
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.FIRST
    e_obj += EnumTest.SECOND
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.FIRST
    e_obj += 2
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.FIRST
    e_obj += "SECOND"
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.SECOND + EnumTest.SECOND
    assert e_obj == EnumTest.FOURTH

    e_obj = EnumTest.FIRST + EnumTest.SECOND + EnumTest.FIRST
    assert e_obj == EnumTest.FOURTH
    
    e_obj = EnumTest.FIRST + NormalEnum.SECOND + EnumTest.FIRST
    assert e_obj == EnumTest.FOURTH

    e_obj = EnumTest.SECOND + 1
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.SECOND + 'FIRST'
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.SECOND + 'EnumTest.FIRST'
    assert e_obj == EnumTest.THIRD

    e_obj = EnumTest.FIRST + 'EnumTest.FIRST' + 2
    assert e_obj == EnumTest.FOURTH

    e_obj = EnumTest.SECOND + '< EnumTest.FIRST >'
    assert e_obj == EnumTest.THIRD

    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND + EnumTest.THIRD

    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND + "THIRD"

    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND + "nosense"

    with pytest.raises(ValueError):
        e_obj = EnumTest.NONE + 5

    with pytest.raises(ValueError):
        e_obj = EnumTest.NONE + 2.8

    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND
        e_obj += EnumTest.THIRD

    with pytest.raises(TypeError):
        e_obj = EnumTest.SECOND + DummyClass()



def test_sub():
    e_obj = EnumTest.THIRD - EnumTest.SECOND
    assert e_obj == EnumTest.FIRST
    
    e_obj = EnumTest.THIRD - EnumTest.SECOND - EnumTest.FIRST
    assert e_obj == EnumTest.NONE
    
    e_obj = EnumTest.THIRD - NormalEnum.SECOND - EnumTest.FIRST
    assert e_obj == EnumTest.NONE

    e_obj = EnumTest.THIRD
    e_obj -= EnumTest.SECOND
    assert e_obj == EnumTest.FIRST

    e_obj = EnumTest.FOURTH
    e_obj -= EnumTest.SECOND
    e_obj -= 'EnumTest.FIRST'
    e_obj -= 1
    assert e_obj == EnumTest.NONE

    e_obj = EnumTest.FOURTH - EnumTest.SECOND
    assert e_obj == EnumTest.SECOND

    e_obj = EnumTest.SECOND - EnumTest.SECOND
    assert e_obj == EnumTest.NONE

    e_obj = EnumTest.SECOND - 'SECOND'
    assert e_obj == EnumTest.NONE

    e_obj = EnumTest.SECOND - 'EnumTest.SECOND   '
    assert e_obj == EnumTest.NONE

    with pytest.raises(ValueError):
        e_obj = EnumTest.FIRST - EnumTest.FOURTH

    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND - "nosense"

    with pytest.raises(ValueError):
        e_obj = EnumTest.FIRST - 'FOURTH'
    
    with pytest.raises(ValueError):
        e_obj = EnumTest.SECOND
        e_obj -= EnumTest.THIRD

    with pytest.raises(ValueError):
        e_obj = EnumTest.FOURTH - 10

    with pytest.raises(ValueError):
        e_obj = EnumTest.FOURTH - 3.99

    with pytest.raises(TypeError):
        e_obj = EnumTest.SECOND - DummyClass()

def test_hash():
    hash_none = EnumTest.NONE.__hash__()
    hash_one = EnumTest.FIRST.__hash__()
    hash_two = EnumTest.SECOND.__hash__()
    hash_three = EnumTest.THIRD.__hash__()
    hash_four = EnumTest.FOURTH.__hash__()
    assert hash_none == hash(EnumTest.NONE)
    assert hash_one == hash(EnumTest.FIRST)
    assert hash_two == hash(EnumTest.SECOND)
    assert hash_three == hash(EnumTest.THIRD)
    assert hash_four == hash(EnumTest.FOURTH)
    e_set = set()
    e_set.add(EnumTest.NONE)
    e_set.add(EnumTest.FIRST)
    e_set.add(EnumTest.SECOND)
    e_set.add(EnumTest.THIRD)
    e_set.add(EnumTest.FOURTH)
    assert len(e_set) == 5
    e_set.add(EnumTest.NONE)
    e_set.add(EnumTest.FIRST)
    e_set.add(EnumTest.SECOND)
    e_set.add(EnumTest.THIRD)
    e_set.add(EnumTest.FOURTH)
    assert len(e_set) == 5
