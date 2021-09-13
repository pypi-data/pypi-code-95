# 16进制的转化
import binascii


def unhexlify(hex_str):
    """16进制转字符串

    :param hex_str: 16进制字符串
    :type hex_str: [type]
    :return: [description]
    :rtype: [type]
    """
    return binascii.unhexlify(hex_str).decode(errors='ignore')


def hexlify(acsii_str, flag=False):
    """字符串转16进制

    :param acsii_str: 字符串
    :type acsii_str: [type]
    :param flag: 是否大写, defaults to False
    :type flag: bool, optional
    :return: [description]
    :rtype: [type]
    """
    hex_str = binascii.hexlify(acsii_str.encode())
    if flag:
        return hex_str.upper().decode(errors='ignore')
    return hex_str.decode(errors='ignore')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', help='ascii -> 16进制')
    parser.add_argument('-a', help='16进制 -> ascii')
    parser.add_argument('-f', '--flag', default=True,
                        action='store_true', help='大写')

    args = parser.parse_args()
    try:
        if args.a:
            print(unhexlify(args.a))
        elif args.b:
            print(hexlify(args.b, args.flag))
    except Exception as e:
        print(e)
