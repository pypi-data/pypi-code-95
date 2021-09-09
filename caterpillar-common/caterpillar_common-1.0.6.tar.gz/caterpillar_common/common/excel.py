import logging
import pandas as pd

from caterpillar_common.common.log import logger

log = logging.getLogger("caterpillar_common")

class Excel(object):
    def __init__(self,excel):
        self.__excel=excel

    def get_rows(self,sheet_name="",is_dict=False):
        """
        获取excel文件的内容
        :param is_dict: 返回列表元素是否为字典格式
        :return: 1、如果 is_dict 为 True，则返回结果的为一个列表，列表每个元素均为字典格式，excel表格的第一行的元素及为字典的key
                 2、如果 is_dict 为 False， 则返回的结果为一个列表，列表的每个元素也为列表，即二维列表格式
                 3、如果 解析的过程中出错，则返回一个空列表
        """
        try:
            if sheet_name:
                data = pd.read_excel(self.__excel, sheet_name=sheet_name)
            else:
                data = pd.read_excel(self.__excel)
            if is_dict:
                datas=[]
                title=list(data.head())
                for value in data.values:
                    row_data = {}
                    row_data.update(dict(zip(title,value)))
                    datas.append(row_data)
                return datas
            else:
                datas=[]
                datas.append(list(data.head()))
                for value in data.values:
                    datas.append(value)
                return datas
        except Exception as e:
            log.error(f"获取excel文件内容时出错了，错误信息为：{str(e)}")
            return []

