import json


def replace_none_to_empty(params_dict):
    """
    替换字典中为none值的key 改为空字符串
    :param params_dict:
    :return: 更新后的 dict
    """
    temp_dict = dict()
    temp_dict.update(params_dict)
    for (key, value) in params_dict.items():

        if value is None or value == {} or value == []:
            temp_dict[key] = ""

    return temp_dict


def pop_empty_value(params_dict):
    """
    去掉参数中value为空的字段
    :return: 去除空参数后的参数字典
    """
    temp_dict = dict()
    temp_dict.update(params_dict)
    for (key, value) in params_dict.items():
        # 这里列出来写，不要直接用 if value 作为判断结果
        if value is None or value == '' or value == {} or value == []:
            temp_dict.pop(key)
    return temp_dict


def get_plain_text(all_params):
    # 组装原始签名参数按照 key 的 ASCII 升序组装
    temp_list = list()
    for (k, v) in sorted(all_params.items()):
        if not isinstance(v, str):
            v = json.dumps(v, ensure_ascii=False)
        temp_list.append('{}={}'.format(str(k), str(v)))
    plain_text = '&'.join(temp_list)
    return plain_text


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()
