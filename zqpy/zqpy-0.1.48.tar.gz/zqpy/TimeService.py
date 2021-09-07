import time
from datetime import datetime
from threading import Timer

class TimeServiceClass(object):
    def GetFileTime(self, mTime = None):
        return self.GetFormatTime('%Y_%m_%d_%H_%M_%S',mTime)
    
    def GetPrintTimeToAll(self, mTime = None):
        return self.GetFormatTime('%Y-%m-%d %H:%M:%S',mTime)
        
    def GetPrintTimeToDay(self, mTime = None):
        return self.GetFormatTime('%Y-%m-%d',mTime)

    def GetFormatTime(self, mFormat, mTime = None):
        if mTime == None:
            mTime = time.localtime()
        return time.strftime(mFormat,mTime)

    def GetLocalTime(self):
        return time.localtime()

    def GetTimeToInt(self):
        return int(time.time())

    def Sleep(self, sleep = 0):
        time.sleep(sleep)

    def TimeToStr(self, timeStamp, formatStr = "%Y--%m--%d %H:%M:%S"):
        timeArray = time.localtime(int(timeStamp))
        otherStyleTime = time.strftime(formatStr, timeArray)
        return otherStyleTime   # 2013--10--10 23:40:00

    """根据日期获取某天凌晨时间"""
    def GetDayZeroTime(self, date):
        if not date:
            return 0
        date_zero = datetime.now().replace(year=date.year, month=date.month,
                                                    day=date.day, hour=0, minute=0, second=0)
        date_zero_time = int(time.mktime(date_zero.timetuple())) * 1000
        return date_zero_time

    """根据日期获取当天凌晨时间  isSecond 是否是秒 """
    def GetCurrDayZeroTime(self, isSecond):
        # 今天的日期
        today_date = datetime.now().date()
        # 今天的零点
        ms = self.GetDayZeroTime(today_date) 
        if isSecond:
            return int(ms/1000)
        return ms

    def GetCurrTime(self):
        return datetime.datetime.now()
    
    def GetNextTime(self, year=None, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        return self.GetCurrTime()+datetime.timedelta(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond, tzinfo=tzinfo)