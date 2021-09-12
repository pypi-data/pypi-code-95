"""
包括comtradeParser一个类

Classes
----------
comtradeParser: 通过输入符合comtrade规范的文件名，对数据内容进行输出

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_comtradeParser import comtradeParser

"""

import struct
import re
import os

import numpy as np  # 1.18.5
import pandas as pd  # 1.1.0


class comtradeParser:
	"""
	通过输入符合comtrade规范的文件名，对数据内容进行输出

	[1] 参数
	_filePath:
		str, cfg/dat文件的路径，形如G://#31机误上电//1//20150214224936

	[2] 返回
	datFile_Binary2Int:
		dataframe， 以cfg为列名称的dataframe格式dat文件内容， 列为“序号， 时间戳， 列1， 列2……”

	[3] 示例1
	>>> filePath = 'G://#31机误上电//1//20150214224936'
	>>> rec = ComtradeParser(_filePath=filePath)
	>>> print(rec.datFile_Binary2Int)
	"""
	def __init__(self, _filePath: str):
		# 初始化一个CFG对象
		self.cfgObj = Cfg()
		# 定义cfg与dat文件及路径
		if os.path.isfile(_filePath + '.cfg'):
			self.cfgObj.cfgFilePath = _filePath + '.cfg'
		else:
			self.cfgObj.cfgFilePath = _filePath + '.CFG'
		if os.path.isfile(_filePath + '.dat'):
			self.cfgObj.datFilePath = _filePath + '.dat'
		else:
			self.cfgObj.datFilePath = _filePath + '.DAT'
		# 解析cfg文件
		with open(self.cfgObj.cfgFilePath, 'r') as cfgFile:
			cache_lineNum = 0
			# 解析CFG文件第一行
			_rowCache = cfgFile.readline().split(',')
			self.cfgObj.stationName, self.cfgObj.stationCode, self.cfgObj.comtradeRev = [_rowCache[i] for i in range(3)]
			# 解析CFG文件第二行
			_rowCache = cfgFile.readline().split(',')
			self.cfgObj.variablesQuant = int(_rowCache[0])
			self.cfgObj.analogQuant = int(_rowCache[1].replace('A', ''))
			self.cfgObj.digitQuant = int(_rowCache[2].replace('D', '').replace('\n', ''))
			# 解析CFG变量配置表
			cache_lineNum += 1
			# 处理模拟量
			for i in range(self.cfgObj.analogQuant):
				_rowCache = cfgFile.readline().split(',')
				self.cfgObj.updateChannels_analog(_index=_rowCache[0], _name=_rowCache[1], _phase=_rowCache[2],
				                                  _target=_rowCache[3], _unit=_rowCache[4], _a=float(_rowCache[5]),
				                                  _b=float(_rowCache[6]), _skew=_rowCache[7], _min=_rowCache[8],
				                                  _max=_rowCache[9], _primary=_rowCache[10], _decondary=_rowCache[11],
				                                  _ps=_rowCache[12])
			# 处理开关量
			for i in range(self.cfgObj.digitQuant):
				_rowCache = cfgFile.readline().split(',')
				self.cfgObj.updateChannels_digit(_index=_rowCache[0], _name=_rowCache[1], _phase=_rowCache[2],
				                                 _target=_rowCache[3], _status=_rowCache[4])
			self.cfgObj.lineFreq = int(cfgFile.readline())
			self.cfgObj.freqQuant = int(cfgFile.readline())
			# 处理其它配置项
			for i in range(self.cfgObj.freqQuant):
				_cache = cfgFile.readline().replace('\n', '').split(',')
				_cache = [int(item) for item in _cache]
				self.cfgObj.others.freqSamples.append(_cache)
			_timestamp1 = cfgFile.readline()
			_timestamp2 = cfgFile.readline()
			_dateFormat = "([0-9]{1,2})/([0-9]{1,2})/([0-9]{2,4}),([0-9]{1,2}):([0-9]{1,2}):([0-9]{1,2})"
			self.cfgObj.others.timestamp1 = timeTransByFormat(_timestamp1, _dateFormat)
			self.cfgObj.others.timestamp2 = timeTransByFormat(_timestamp2, _dateFormat)
			self.cfgObj.others.dateFormat = cfgFile.readline()
			self.cfgObj.others.timeMult = int(float(cfgFile.readline().replace('\n', '')))
		self.datFile_Binary2Int = self.parseDatFile_binary()
		self.transferTs()
		self.transferDat()

	def transferDat(self):
		for i in range(2, self.cfgObj.analogQuant + 2):
			self.datFile_Binary2Int.iloc[:, i] = self.datFile_Binary2Int.iloc[:, i] * self.cfgObj.analog.a[i - 2] + \
			                                     self.cfgObj.analog.b[i - 2]

	def transferTs(self, _ts_basic=1e-6, _ts_mult=1):
		timestamp = self.datFile_Binary2Int.iloc[:, 1] * _ts_basic * _ts_mult
		self.datFile_Binary2Int.iloc[:, 1] = timestamp

	def parseDatFile_binary(self):
		"""
		输出DF格式的.dat文件中的所有数据，列名为变量名称，并包括【序号】【时间戳】两列
		"""
		indexBytes = 4
		timeSerieBytes = 4
		analogBytes = 2
		digitBytes = 2
		# 判断是否有开关量并计算每次读取的数据长度
		if self.cfgObj.variablesQuant == self.cfgObj.analogQuant:
			structFormat = "LL {analogQuant:d}h"
		elif self.cfgObj.variablesQuant == self.cfgObj.digitQuant:
			structFormat = "LL {digitQuant:d}H"
		else:
			structFormat = "LL {analogQuant:d}h {digitQuant:d}H"
		readLength = int(indexBytes +
		                 timeSerieBytes +
		                 analogBytes * self.cfgObj.analogQuant +
		                 digitBytes * self.cfgObj.digitQuant/16)
		# 读取数据
		columns = ['序号', '时间戳'] + self.cfgObj.analog.name + self.cfgObj.digit.name
		output = []
		with open(self.cfgObj.datFilePath, 'rb') as datFile:
			while True:
				try:
					res1 = []
					res2 = []
					content = datFile.read(readLength)
					pattern = structFormat.format(analogQuant=self.cfgObj.analogQuant, digitQuant=int(self.cfgObj.digitQuant/16))
					reader = struct.Struct(pattern)
					samples = reader.unpack(content)
					eachRow_analogData = list(samples)[0:self.cfgObj.analogQuant + 2]
					res1 = res1 + eachRow_analogData
					eachRow_digitData_notParsed = list(samples)[self.cfgObj.analogQuant + 2:None]
					for i in range(np.shape(eachRow_digitData_notParsed)[0]):
						cache = eachRow_digitData_notParsed[i]
						endLocOfEachRead = min([(i + 1) * 16, self.cfgObj.digitQuant])
						for j in range(i * 16, endLocOfEachRead):
							leftMoved = int('0b01', 2) << j - i * 16
							eachRow_digitData_parsed = (cache & leftMoved) >> j - i * 16
							res2.append(eachRow_digitData_parsed)
					output.append([res1 + res2][0])
				except:
					break
		return pd.DataFrame(output, columns=columns)


def timeTransByFormat(_timeStr: str, _format: str) -> tuple:
	pattern = re.compile(_format)
	res = pattern.match(_timeStr)
	day = res.group(1)
	month = res.group(2)
	year = res.group(3)
	hour = res.group(4)
	minute = res.group(5)
	second = res.group(6)
	return year, month, day, hour, minute, second


class Cfg:
	def __init__(self, **kwargs):
		self.variablesQuant = 0
		self.cfgFilePath = ''
		self.datFilePath = ''
		kwargsDict = kwargs.keys()
		self.stationName = None if '_stationName' not in kwargsDict else kwargs['_stationName']
		self.stationCode = None if '_stationCode' not in kwargsDict else kwargs['_stationCode']
		self.comtradeRev = None if '_comtradeRev' not in kwargsDict else kwargs['_comtradeRev']
		self.varsQuant = None if '_varsQuant' not in kwargsDict else kwargs['_varsQuant']
		self.analogQuant = None if '_analogQuant' not in kwargsDict else kwargs['_analogQuant']
		self.digitQuant = None if '_digitQuant' not in kwargsDict else kwargs['_digitQuant']
		self.analog = analog()
		self.digit = digit()
		self.others = others()

	def updateChannels_analog(self, **kwargs):
		kwargsDict = kwargs.keys()
		self.analog.index.append([] if '_index' not in kwargsDict else kwargs['_index'])
		self.analog.name.append([] if '_name' not in kwargsDict else kwargs['_name'])
		self.analog.phase.append([] if '_phase' not in kwargsDict else kwargs['_phase'])
		self.analog.target.append([] if '_target' not in kwargsDict else kwargs['_target'])
		self.analog.unit.append([] if '_unit' not in kwargsDict else kwargs['_unit'])
		self.analog.a.append([] if '_a' not in kwargsDict else kwargs['_a'])
		self.analog.b.append([] if '_b' not in kwargsDict else kwargs['_b'])
		self.analog.skew.append([] if '_skew' not in kwargsDict else kwargs['_skew'])
		self.analog.min.append([] if '_min' not in kwargsDict else kwargs['_min'])
		self.analog.max.append([] if '_max' not in kwargsDict else kwargs['_max'])
		self.analog.primary.append([] if '_primary' not in kwargsDict else kwargs['_primary'])
		self.analog.secondary.append([] if '_secondary' not in kwargsDict else kwargs['_secondary'])
		self.analog.ps.append([] if '_ps' not in kwargsDict else kwargs['_ps'])

	def updateChannels_digit(self, **kwargs):
		kwargsDict = kwargs.keys()
		self.digit.index.append([] if '_index' not in kwargsDict else kwargs['_index'])
		self.digit.name.append([] if '_name' not in kwargsDict else kwargs['_name'])
		self.digit.phase.append([] if '_phase' not in kwargsDict else kwargs['_phase'])
		self.digit.target.append([] if '_target' not in kwargsDict else kwargs['_target'])
		self.digit.status.append([] if '_status' not in kwargsDict else kwargs['_status'])


class analog:
	def __init__(self, **kwargs):
		kwargsDict = kwargs.keys()
		self.index = [] if '_index' not in kwargsDict else kwargs['_index']
		self.name = [] if '_name' not in kwargsDict else kwargs['_name']
		self.phase = [] if '_phase' not in kwargsDict else kwargs['_phase']
		self.target = [] if '_target' not in kwargsDict else kwargs['_target']
		self.unit = [] if '_unit' not in kwargsDict else kwargs['_unit']
		self.a = [] if '_a' not in kwargsDict else kwargs['_a']
		self.b = [] if '_b' not in kwargsDict else kwargs['_b']
		self.skew = [] if '_skew' not in kwargsDict else kwargs['_skew']
		self.min = [] if '_min' not in kwargsDict else kwargs['_min']
		self.max = [] if '_max' not in kwargsDict else kwargs['_max']
		self.primary = [] if '_primary' not in kwargsDict else kwargs['_primary']
		self.secondary = [] if '_secondary' not in kwargsDict else kwargs['_secondary']
		self.ps = [] if '_ps' not in kwargsDict else kwargs['_ps']


class digit:
	def __init__(self, **kwargs):
		kwargsDict = kwargs.keys()
		self.index = [] if '_index' not in kwargsDict else kwargs['_index']
		self.name = [] if '_name' not in kwargsDict else kwargs['_name']
		self.phase = [] if '_phase' not in kwargsDict else kwargs['_phase']
		self.target = [] if '_target' not in kwargsDict else kwargs['_target']
		self.status = [] if '_status' not in kwargsDict else kwargs['_status']


class others:
	def __init__(self, **kwargs):
		kwargsDict = kwargs.keys()
		self.lineFreq = None if '_lineFreq' not in kwargsDict else kwargs['_lineFreq']
		self.freqQuant = None if '_freqQuant' not in kwargsDict else kwargs['_freqQuant']
		self.freqSamples = [] if '_freqSamples' not in kwargsDict else kwargs['_freqSamples']
		self.timestamp1 = [] if '_timestamp1' not in kwargsDict else kwargs['_timestamp1']
		self.timestamp2 = [] if '_timestamp2' not in kwargsDict else kwargs['_timestamp2']
		self.dateFormat = [] if '_dateFormat' not in kwargsDict else kwargs['_dateFormat']
		self.timeMult = [] if '_timeMult' not in kwargsDict else kwargs['_timeMult']