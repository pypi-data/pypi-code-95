import base64
import json
import re


def get_encode_type(txt):
    """判断文本的加密类型

    :param txt: 任意文本
    :type txt: str
    :return: 加密类型
    :rtype: str
    """
    base64_ptn = re.compile(r'^[a-zA-Z0-9+/]+=*?$')

    if len(txt) % 4 == 0 and base64_ptn.match(txt):
        return 'BASE64'

    json_ptn = re.compile(r'^\{[\w\":,-\\\(\)]+?\}$')
    if json_ptn.match(txt):
        return 'JSON'

    return None


def auto_decode(txt):
    """自动解密字符串

    :param txt: 加密字符串
    :type txt: str
    :return: 解密内容
    :rtype: str
    """
    encode_type = get_encode_type(txt)

    if encode_type == 'BASE64':
        return decode_with_base64(txt)
    elif encode_type == 'JSON':
        return decode_with_json(txt)
    else:
        return txt


def decode_with_base64(txt):
    """解密base64字符串

    :param txt: base64加密的字符串
    :type txt: str
    :return: 解密后的文本
    :rtype: str
    """
    try:
        return base64.b64decode(txt.encode()).decode('utf-8')
    except UnicodeDecodeError:
        result = base64.b64decode(txt.encode()).decode(
            'utf-8', errors='ignore')
        print('Could not decode with base64: {}'.format(result))


def decode_with_json(txt):
    """解码json字符串，主要用于还原unicode编码的中文字符

    :param txt: json字符串
    :type txt: str
    :return: json格式的数据
    :rtype: str
    """
    return json.loads(txt)
