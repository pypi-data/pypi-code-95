import base64


def decode_with_base64(txt):
    """解密base64字符串

    :param txt: base64加密的字符串
    :type txt: str
    :return: 解密后的文本
    :rtype: str
    """
    try:
        return base64.b64decode(txt.encode()).decode('utf-8', errors='ignore')
    except UnicodeDecodeError:
        return None
