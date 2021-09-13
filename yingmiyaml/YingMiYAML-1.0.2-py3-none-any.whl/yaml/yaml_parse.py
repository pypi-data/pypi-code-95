# coding=utf8
# @Created : 2021/6/24 1:12 下午
# @Author  : liuyf@yingmi.cn

import os
import yaml
from .variables import profile_name, profile_sep, default_profile_key
from .nested_dict_value import get_dict_value as get_nested_dict_value, dict_update as nested_dict_update

_profile_list_key = '$profile_list_'


def _profile_key(profile):
    return profile_name + '-' + profile


def parse_yaml(yaml_file) -> dict:
    """
    解析yaml文件，使用---分割多个profile，使用$profiles指定每段profile的名称
    :param yaml_file:
    :return:
    """
    if not os.path.isfile(yaml_file):
        raise FileNotFoundError("%s not found" % yaml_file)

    yaml_list = {_profile_list_key: []}
    with open(yaml_file, 'r') as file:
        lines = file.read()
        lines = lines.split(profile_sep)
        for line in lines:
            content = yaml.load(line, Loader=yaml.FullLoader)
            if profile_name in content:
                profiles = content[profile_name]
                yaml_list[_profile_key(profiles)] = content
                yaml_list[_profile_list_key].append(profiles)
            else:
                yaml_list.update(content)

    return yaml_list


def get_env_profile(data: dict, active_profile: str = None) -> dict:
    """
    如果没有指定profile，则从app.profile.active获取，如果两个都没有，则取第一个profile
    :param data:
    :param active_profile: 指定profile
    :return:
    """
    # 解析出来的profile
    profile_list = data.get(_profile_list_key)
    first_profile = None

    if len(profile_list) == 0:
        return data
    else:
        first_profile = profile_list[0]

    if active_profile is None:
        active_profile = get_nested_dict_value(data, default_profile_key)

    if active_profile is None:
        active_profile = first_profile

    data = data.copy()
    # 删除不需要的profile，将选则的profile合并到一起
    for p in profile_list:
        profile_name_ = _profile_key(p)
        if p != active_profile:
            data.pop(profile_name_)
        else:
            nested_dict_update(data, data.get(profile_name_))
            data.pop(profile_name_)
    data.pop(_profile_list_key)
    return data

