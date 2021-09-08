import os
import sys

import xml.dom.minidom
from datetime import datetime

from SapphireQuant.Core import Holiday


class HolidayHelper:
    """
    节假日
    """
    FileName = "Holiday.xml"
    _holiday_map = None
    _holidays = None
    IsLoaded = False

    @staticmethod
    def get_all_china_holidays():
        """
        加载配置
        """
        if not HolidayHelper.IsLoaded:
            try:
                config_directory = os.path.join(sys.modules['ROOT_DIR'], 'Profiles')
                path = os.path.join(config_directory, HolidayHelper.FileName)
                if os.path.exists(path):
                    pass
                else:
                    print("未找到配置文件:" + path)

                HolidayHelper._holidays = []
                HolidayHelper._holiday_map = {}
                _root = xml.dom.minidom.parse(path).documentElement
                holiday_nodes = _root.getElementsByTagName('Holiday')
                for holiday_node in holiday_nodes:
                    holiday = Holiday()
                    holiday.name = holiday_node.getAttribute('name')
                    holiday.pre_holiday_trading_date = datetime.strptime(holiday_node.getAttribute('pre_holiday_trading_date'), '%Y%m%d')
                    holiday.begin_date = datetime.strptime(holiday_node.getAttribute('begin_date'), '%Y%m%d')
                    holiday.end_date = datetime.strptime(holiday_node.getAttribute('end_date'), '%Y%m%d')
                    holiday.post_holiday_trading_date = datetime.strptime(holiday_node.getAttribute('post_holiday_trading_date'), '%Y%m%d')
                    HolidayHelper._holidays.append(holiday)
                    HolidayHelper._holiday_map[holiday.post_holiday_trading_date] = holiday

                HolidayHelper.IsLoaded = True
            except Exception as e:
                print(str(e))
        pass

    @staticmethod
    def holidays():
        """
        节假日
        :return:
        """
        if HolidayHelper._holidays is None:
            HolidayHelper.get_all_china_holidays()
        return HolidayHelper._holidays

    @staticmethod
    def is_post_holiday_trading_date(date):
        """
        是否为节假日后第一个交易日
        :return:
        """
        if HolidayHelper._holidays is None:
            HolidayHelper.get_all_china_holidays()

        if date in HolidayHelper._holiday_map.keys():
            return True
        return False

# date = datetime(2020,1,2)
# a = HolidayHelper.is_post_holiday_trading_date(date)
# print(a)
