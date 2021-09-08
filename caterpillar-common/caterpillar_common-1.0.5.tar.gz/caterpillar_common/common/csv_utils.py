import csv
import logging
from pathlib import Path

from caterpillar_common.common.log import logger

log = logging.getLogger("caterpillar_common")


class CSV(object):
    def __init__(self, csv_file=""):
        self.__csv_file = csv_file

    def write_row(self, data, head="", mode="a+"):
        if isinstance(data, dict):
            try:
                is_empty=self.is_empty()
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.DictWriter(f, fieldnames=head or data.keys())
                    if is_empty:
                        csv_writer.writeheader()
                    csv_writer.writerow(data)
            except Exception as e:
                log.error(
                    f"向csv文件写入一行字典数据失败，csv文件为：{self.__csv_file}, 行数据为：{data}, 写入模式为：{mode}，标题信息为：{head}。报错信息如下：{str(e)}")
        else:
            try:
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(data)
            except Exception as e:
                log.error(
                    f"向csv文件写入一行列表数据失败，csv文件为：{self.__csv_file}, 行数据为：{data}, 写入模式为：{mode}。报错信息如下：{str(e)}")

    def write_rows(self, datas, head="", mode="a+"):

        if len(datas) == 0:
            return
        if isinstance(datas[0],dict):
            try:
                is_empty=self.is_empty()
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.DictWriter(f, fieldnames=head or list(datas[0].keys()))
                    if is_empty:
                        csv_writer.writeheader()
                    csv_writer.writerows(datas)
            except Exception as e:
                log.error(
                    f"向csv文件写入多行字典数据失败，csv文件为：{self.__csv_file}, 第一行数据为：{datas[0]}, 写入模式为：{mode}，标题信息为：{head}。报错信息如下：{str(e)}")
        else:
            try:
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(datas)
            except Exception as e:
                log.error(
                    f"向csv文件写入多行列表数据失败，csv文件为：{self.__csv_file}, 行数据为：{datas}, 写入模式为：{mode}。报错信息如下：{str(e)}")

    def get_rows(self,is_dict=False):
        """
        获取csv文件的内容
        :param is_dict: 返回列表元素是否为字典格式
        :return: 1、如果 is_dict 为 True，则返回结果的为一个列表，列表每个元素均为字典格式，csv表格的第一行的元素及为字典的key
                 2、如果 is_dict 为 False， 则返回的结果为一个列表，列表的每个元素也为列表，及二维列表格式
                 3、如果 解析的过程中出错，则返回一个空列表
        """
        try:
            if is_dict:
                with open(self.__csv_file,"r",encoding="utf8",newline="") as f:
                    return list(csv.DictReader(f))
            else:
                with open(self.__csv_file,"r",encoding="utf8",newline="") as f:
                    return list(csv.reader(f))
        except Exception as e:
            log.error(f"获取csv文件内容时出错了，错误信息为：{str(e)}")
            return []

    def is_empty(self):
        """
        判断csv文件是否为空
        :return: 1、如果文件不存在，返回True
                 2、如果文件存在，内容为空，则返回True
                 3、如果文件内容行数大于0，返回False，行数等于0返回True
                 4、如果在计算csv文件内容函数的时候出现了异常，则也返回True
        """
        try:
            if not Path(self.__csv_file).exists():
                return True
            return len(self.get_rows())==0
        except Exception as e:
            log.error(f"在判断csv文件是否为空时出现异常，异常信息为：{str(e)}")
            return True
