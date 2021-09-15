import random
import time
import datetime


def generate_mer_order_id():
    """
    生成请求order_no，根据时间戳+6位随机数
    :param product_id:
    :param huifu_id:
    :return:
    """
    timestamp = str(int(time.time()))
    return "" + timestamp + str(random.randint(100000, 9999999))


def generate_req_date():
    """
    获取当前日期，格式%Y%m%d
    :return: 日期
    """
    return datetime.datetime.now().strftime('%Y%m%d')
