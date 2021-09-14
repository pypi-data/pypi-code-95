import os
import socket
import logging

BYTES_MAP = {
    "TB": 40,
    "GB": 30,
    "MB": 20,
    "KB": 10,
    "B" :  1,
}
# 数字以Bytes大小展示，比如12(B), 12.2(MB), 12.2(GB)
def digit_to_bytescount(digit: int):
    assert digit >= 0
    for i in BYTES_MAP:
        v = digit >> BYTES_MAP[i]
        if v:
            res = float(digit) / (1 << BYTES_MAP[i])
            return ("%.1f(%s)" % (res, i))
    return "0(B)"

# 作用等效于tree命令
def walk_through_dir(path):
    if os.path.isfile(path):
        logging.info("F_{}".format(path))
    elif os.path.isdir(path):
        logging.info("D_{}/".format(path))
        for path_sub in os.listdir(path):
            walk_through_dir(os.path.join(path, path_sub))

# 获取当前环境的ip
def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
        return ip