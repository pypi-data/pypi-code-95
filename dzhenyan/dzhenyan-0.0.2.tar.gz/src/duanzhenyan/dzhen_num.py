from __future__ import division, absolute_import

__all__ = ['str_2_num']


def str_2_num(s: str):
    """
    This function is become str into num,
    eg: 100+ to 100 ..
    :param s: input string
    :return: oout string the type is num
    """
    try:
        if isinstance(s, str):
            return s.replace('+', '')
        else:
            return s
    except KeyError:
        raise Exception('type is error')
