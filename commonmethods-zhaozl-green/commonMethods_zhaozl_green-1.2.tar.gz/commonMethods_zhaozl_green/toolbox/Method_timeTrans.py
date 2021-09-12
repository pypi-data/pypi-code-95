"""
包括timeTrans

Classes
----------
timeTrans: 通过输入list(int)或者int形式的时间戳unixTimestamp，与形如'%Y/%m/%d %H:%M:%S'的formation，对时间戳进行计算并输出string

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_timeTrans import timeTrans

"""

import time


class timeTrans:
	"""
	通过输入list(int)或者int形式的时间戳unixTimestamp，与形如'%Y/%m/%d %H:%M:%S'的formation，对时间戳进行计算并输出string

	[1] 参数
	----------
	unixTime:
		int/list(int), 秒级或毫秒级时间，形如1616059398000或[1617159398000, 1617259398000, 1617359398000, 1617359398]
	format:
		str/None, 输出时间字符串的格式, optional, default %Y/%m/%d %H:%M:%S

	[2] 返回
	-------
	timeStr:
		str, 输出时间字符串, 如2015/01/12 09:15:00

	[3] 示例1
	--------
	>>> timestamp = [1617159398000, 1617259398000, 1617359398000, 1617359398]
	>>> obj = timeTrans(unixTime=timestamp, format='%Y/%m/%d %H:%M:%S')
	>>> print(obj.timeStr)
	"""

	def __init__(self, **kwargs):
		def unixTime2strTime(_unixTime, _format):
			unixTimeLength = len(str(_unixTime))
			second = _unixTime if unixTimeLength == 10 else _unixTime / 1000
			_strTime = time.strftime(_format, time.localtime(second))
			return _strTime

		self.unixTime = kwargs['unixTime']
		self.format = kwargs['format'] if 'format' in kwargs.keys() else "%Y-%m-%d %H:%M:%S"
		isInt = isinstance(self.unixTime, int)
		isList = isinstance(self.unixTime, list)
		if isInt:
			self.timeStr = unixTime2strTime(self.unixTime, self.format)
		elif isList:
			timeStr = []
			for item in self.unixTime:
				_timeStr = unixTime2strTime(item, self.format)
				timeStr.append(_timeStr)
			self.timeStr = timeStr
		else:
			self.timeStr = None