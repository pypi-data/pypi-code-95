"""
包括processBar一个类

Classes
----------
processBar: 在打印的循环体中输出进度条

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_processBar import processBar

"""

import sys
import time
import warnings
import numpy as np


class processBar:
	"""
	在打印的循环体中输出进度条

	[1] 参数
	----------
	_processBarFormat:
		str, 进度条样式, optional, %3.0f:表示百分比字符串所在位置,%s:表示进度条所在位置, default "\r【%3.0f%%】 |%s|"
	_reachedSymbol:
		str, 进度条已执行时的样式, 一个字符, optional, default "█"
	_notReachedSymbol:
		str, 进度条未执行时的样式, 一个字符, optional, default " "
	_dataQuant:
		int, 数据总量
	_processBarLength:
		int, 进度条总长度, optional, default 100
	_showRemainingTime:
		bool, 是否需要展示剩余时间, optional, default False
	_remainTimeFormat:
		str, 剩余时间的格式, optional, default '\t%8.1f s'

	[2] 方法
	----------
	_refresh:
		更新一次进度条

	[3] 示例1
	--------
	>>> barObj = processBar(_dataQuant=10000, _processBarLength=50)
	>>> for i in range(10000):
	>>>     barObj.refresh()

	[4] 示例2
	--------
	>>> barObj = processBar(_dataQuant=targetData.shape[0], _processBarLength=50, _showRemainingTime=True, _remainTimeFormat='Remain：%8.2f 秒 ')
	>>> for i in range(10000):
	>>>     barObj.refresh()

	"""

	def __init__(self, **kwargs):
		if '_dataQuant' not in kwargs.keys():
			warnings.warn('需要输入变量【_dataQuant】以定义数据总量')
			exit(-1)
		self.dataQuant = kwargs['_dataQuant']
		self.processBarLength = 100 if '_processBarLength' not in kwargs.keys() else kwargs['_processBarLength']
		self.reachedSymbol = "█" if "_reachedSymbol" not in kwargs.keys() else kwargs['_reachedSymbol']
		self.notReachedSymbol = " " if "_notReachedSymbol" not in kwargs.keys() else kwargs['_notReachedSymbol']
		self.format = "\r【%3.0f%%】 |%s|" if '_processBarFormat' not in kwargs.keys() else kwargs['_processBarFormat']
		self.__alreadyWalkedDataQuant = 0
		self.__showRemainingTime = False if "_showRemainingTime" not in kwargs.keys() else kwargs['_showRemainingTime']
		self.__startTime = time.time()
		self.__nowTime = None
		if self.__showRemainingTime:
			self.remainTimeFormat = '\t%8.1f s' if '_remainTimeFormat' not in kwargs.keys() else kwargs['_remainTimeFormat']
			self.format = self.format + self.remainTimeFormat

	def refresh(self):
		if self.__showRemainingTime:
			self.__nowTime = time.time()
		self.__alreadyWalkedDataQuant += 1
		_percent = self.__alreadyWalkedDataQuant / self.dataQuant
		__walkedLength = int(np.floor(_percent * self.processBarLength))
		__notWalkedLength = int(self.processBarLength - __walkedLength)
		_processBar = self.reachedSymbol * __walkedLength + self.notReachedSymbol * __notWalkedLength
		if self.__showRemainingTime:
			sys.stdout.write(self.format % (_percent * 100, _processBar, (self.__nowTime - self.__startTime) / (__walkedLength+0.001) * __notWalkedLength))
		else:
			sys.stdout.write(self.format % (_percent * 100, _processBar))
		if _percent == 1:
			sys.stdout.write("\n")
