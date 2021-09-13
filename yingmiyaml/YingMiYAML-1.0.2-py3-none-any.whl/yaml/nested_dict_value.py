# coding=utf8
# @Created : 2021/6/25 12:12 下午
# @Author  : liuyf@yingmi.cn
import re
import collections.abc


def get_dict_value(data: dict, keys: str, default=None) -> object:
    """
    获取多级key指定的值

    >>> a = {'c': {'b': 'this b', 'd': [1, {'f': 'cffff', 'e': ['a', 2, 3, 'd']}, 3, 4]}}
    >>> get_dict_value(a, 'c.b')
    'this b'
    >>> get_dict_value(a, 'c.d.[1]') == a['c']['d'][1]
    True
    >>> get_dict_value(a, 'c.d.[1].f')
    'cffff'
    >>> get_dict_value(a, 'c.d.[1].e.[2]')
    3

    :param data: 取值对象，字典类型
    :param keys: 取值key，支持多级，以.分割
    :param default: 不存在时返回的默认值
    :return:

    """
    keys_list = keys.split('.')
    dictionary = dict(data)
    for key in keys_list:
        # 按照keys_list顺序循环键值
        try:
            if isinstance(dictionary, list) and re.match(r'\[(\d+)\]', key):
                index = re.match(r'\[(\d+)\]', key).group(1)
                dict_values = dictionary[int(index)]
            elif key in dictionary:
                dict_values = dictionary.get(key)
            elif key.isnumeric():
                dict_values = dictionary.get(int(key))
            else:
                dict_values = default
        except IndexError as ie:
            raise ie
        except:
            return default
            # 如果字符串型的键转换整数型错误，返回None
        dictionary = dict_values
    return dictionary


def dict_update(d: dict, u: dict):
    """
    多级数组合并

    >>> source = {'name': 'this name source', 'groups': {'a':[1, 2, 3], 'b': [4, 5, 6]}, 'age': '>10'}
    >>> update_data = {'age': '>20', 'groups':{'b':[4, 5, 6, 7]}}
    >>> dict_update(source, update_data) == source
    >>> source['groups']['a'][2]
    3
    >>> source['groups']['b'][3] == update_data['groups']['b'][3]
    True
    >>> source['groups']['b'][3]
    7

    :param d: 需要被修改的dict
    :param u: 修改部分
    :return: 返回修改后的dict
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d
