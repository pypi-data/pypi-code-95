# coding=utf-8
import time
import socket


def parse_time(timestamp):
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    except Exception:
        return "0000-00-00 00:00:00"


def get_time():
    return parse_time(time.time())


# 获取IP用
flat = (lambda L: sum(map(flat, L), []) if isinstance(L, list) or isinstance(L, tuple) else [L])


def get_hostname():
    try:
        return ";".join(flat(socket.gethostbyname_ex(socket.gethostname())))
    except Exception:
        # 某些情况下可能会出错
        return socket.gethostname()


if __name__ == '__main__':
    from future import print_function
    print(get_time())
