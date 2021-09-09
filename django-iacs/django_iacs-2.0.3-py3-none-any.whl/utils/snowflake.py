import hashlib

from django.utils import timezone

timestamp_bit = 31

host_max_bit = 5

auto_increase_bit = 16

total_bit = timestamp_bit + host_max_bit + auto_increase_bit

auto_increase = 0

last_timestamp = 0


def get_timestamp():
    """
    :return: 秒级时间戳
    """
    return int(timezone.now().timestamp())


def snowflake(host_id=1):
    """
    snowflake算法的简化实现
    ====================

    :param host_id:
    :return:
    """
    current_timestamp = get_timestamp()  # 16

    if host_id >= 2 ** host_max_bit:
        raise Exception(f'host_id out of range, {host_id}')

    result = (current_timestamp << host_max_bit) + host_id

    global auto_increase, last_timestamp

    if current_timestamp == last_timestamp:
        auto_increase += 1

        if auto_increase >= 2 ** auto_increase_bit:
            raise Exception('boom, out of range')
    else:
        auto_increase = 0

    last_timestamp = current_timestamp

    result = (result << auto_increase_bit) + auto_increase

    assert result.bit_length() == total_bit

    return result


def create_token():
    val = snowflake()
    return str(hashlib.md5(str(val).encode("utf-8")).hexdigest())