"""
Functions
----------
* code2Name: 通过输入词典对传入code进行转译同时使用_verbose控制是否显示对字典的预检验
* printWithColor: 打印具有颜色和特定格式的字符串
* mapminmax: 数据进行标准化[0，1]
* moduleOfDataframe: 计算一个dataframe所表达的多个向量的模
* cosineThetaOfVectors: 计算向量1（或多个向量1）与向量2的夹角余弦
* randomGrouping: 根据比例随机取得一数据表中的样本
* proportionalGrouping: 根据比例间隔取得一数据表中的样本，样本不重复，严格按照截取比例间隔抽样选取

Example
----------
>>> from commonMethods_zhaozl import code2Name, printWithColor

"""

import numpy as np  # numpy==1.18.5
import pandas as pd  # pandas==1.1.0
import warnings

pd.set_option('display.max_columns', 10000, 'display.width', 10000, 'max_rows', 50,
              'display.unicode.east_asian_width', True)


def code2Name(_kksCodes: list, _dictNames: list, _kksCode: list, _verbose=True):
	"""
	通过输入词典对传入code进行转译同时使用_verbose控制是否显示对字典的预检验

	[1] 参数
	----------
	_kksCodes:
	    list, 编码的字典
	_dictNames:
	    list, 名称的字典
	_kksCode:
	    list, 需要转译的编码
	_verbose:
	    Boolean, 是否显示对输入字典和待转译编码的检查结果

	[2] 返回
	-------
	-/-:
	    list, 转译完成的名称

	[3] 示例1
	--------
	>>> a = code2Name(kksCode, dictName, ['ED009HP2MUB01UU008AA01J3DG006EA01'])
	>>> print(a)
	"""
	# 检查输入的清单是否符合基本要求
	len_kksCodes = len(_kksCodes)
	len_kksCodes_unique = len(pd.unique(_kksCodes))
	len_dictNames = len(_dictNames)
	len_dictNames_unique = len(pd.unique(_dictNames))
	if _verbose:
		checkStr01 = "待检编码中有重复项 X " if isinstance(_kksCode, list) and len(np.unique(_kksCode)) != len(
			_kksCode) else "待检编码中没有重复项 √ "
		checkStr02 = "编码中没有重复项 √ " if len_kksCodes == len_kksCodes_unique else "编码中有重复项 X "
		checkStr03 = "名称中没有重复项 √ " if len_dictNames == len_dictNames_unique else "名称中有重复项 (允许) "
		print("#" * 2 * (2 + max([len(checkStr01), len(checkStr02), len(checkStr03)])))
		print('\t', checkStr01, '\n\t', checkStr02, '\n\t', checkStr03)
		print("#" * 2 * (2 + max([len(checkStr01), len(checkStr02), len(checkStr03)])))
	# 字典以中文名称为依据，升序排列
	_dict = pd.DataFrame({'kksCodes': _kksCodes, 'dictNames': _dictNames}).sort_values(by=['dictNames'])
	# 查询
	_kksName = []
	if isinstance(_kksCode, list):
		for eachCode_toReplace in _kksCode:
			queryRes = _dict.query("kksCodes.str.contains(\'" + eachCode_toReplace + "\')", engine='python')
			res = queryRes['dictNames'].values
			if np.shape(res)[0] == 0:
				print(">>> 注意：对象kksCode未找到kksName，此kksCode是 %s" % (eachCode_toReplace))
			elif np.shape(res)[0] >= 2:
				print(">>> 错误: 单个kksCode对应了多个kksName，这些kksCode是%s，这些kksName是%s" % (
					queryRes['kksCodes'].values, queryRes['dictNames'].values))
			if res:
				_kksName = _kksName + res.tolist()
			else:
				_kksName.append(eachCode_toReplace)
		return _kksName


def printWithColor(_msg, _prefix="\n\n", _suffix="\n",
                   _displayStyle="default",
                   _fontColor="white",
                   _backColor=None):
	"""
	打印具有颜色和特定格式的字符串

	:param _msg: str, 需要打印的信息
	:param _displayStyle: str, 需要呈现的模式, 可选项, ['default', 'bold', 'italic', 'underline', 'reverse'], default, "default"
	:param _fontColor: str, 字体颜色, 可选项, ['white', 'red', 'green', 'yellow', 'blue', 'purple', 'grey'], default, "white"
	:param _backColor: str, 背景色, 可选项, ['white', 'red', 'green', 'yellow', 'blue', 'purple', 'grey'], default, None
	:param _prefix: str, 前缀
	:param _suffix: str, 后缀
	:returns: e.g printWithColor("11111111111111", _displayStyle='bold', _fontColor='red', _backColor='grey')
	"""
	displayDict = ['default', 'bold', '-', 'italic', 'underline', '-', '-', 'reverse', '-']
	fontDict = ['white', 'red', 'green', 'yellow', 'blue', 'purple', '-', 'grey']
	backDict = ['white', 'red', 'green', 'yellow', 'blue', 'purple', 'cyan', 'grey']
	if _backColor:
		_display = str(displayDict.index(_displayStyle))
		_font = "3" + str(fontDict.index(_fontColor))
		_back = "4" + str(backDict.index(_backColor))
		print(_prefix + "\033[" + _display + ";" + _font + ";" + _back + "m" + _msg + "\033[0m" + _suffix)
	else:
		_display = str(displayDict.index(_displayStyle))
		_font = "3" + str(fontDict.index(_fontColor))
		print(_prefix + "\033[" + _display + ";" + _font + "m" + _msg + "\033[0m" + _suffix)


def mapminmax(_inputData: pd.DataFrame, _scalerMin: list, _scalerMax: list) -> pd.DataFrame:
	"""
	通过如下方式对数据进行标准化

	:math:`res = \\dfrac{ \\vec{v} - min }{ max - min }`

	:param _inputData: dataframe, 需要进行标准化的数据，列为维度，行为样本
	:param _scalerMax: list, 用于进行标准化的各维度最大值
	:param _scalerMin: list, 用于进行标准化的各维度最小值
	:return: dataframe, 标准化后的数据，列为维度，行为样本，columns名称与输入的_inputData的列名称
	"""
	_dataColumns = _inputData.columns
	_cache = np.divide(np.subtract(_inputData.values, _scalerMin), np.subtract(_scalerMax, _scalerMin))
	_output = pd.DataFrame(_cache, columns=_dataColumns)
	return _output.reset_index(drop=True)


def moduleOfDataframe(_dataframe: pd.DataFrame) -> np.array:
	"""
	计算一个dataframe所表达的多个向量的模

	:param _dataframe: dataframe, 需要进行模计算的数据表，列为维度，行为样本
	:return: np.array, 模
	"""
	return np.sqrt(np.sum(np.matmul(np.asmatrix(_dataframe.values), np.transpose(_dataframe.values)), axis=0))


def cosineThetaOfVectors(_vector01: pd.DataFrame, _vector02: pd.DataFrame) -> list:
	"""
	计算向量1（或多个向量1）与向量2的夹角余弦

	:param _vector01: dataframe, 需要进行夹角计算的向量1，列为维度，行为样本，可以为多个样本
	:param _vector02: dataframe, 需要进行夹角计算的向量2，列为维度，行为样本，必须为单一样本
	:return: list，向量1（或多个向量1）与向量2的夹角余弦
	"""
	_matmul = np.matmul(np.asmatrix(_vector01.values), np.transpose(_vector02.values))
	_vector01_mod = moduleOfDataframe(_vector01)
	_vector02_mod = moduleOfDataframe(_vector02)
	_matmul_mod = np.matmul(_vector01_mod.transpose(), _vector02_mod).transpose()
	_cosineTheta = np.divide(_matmul.transpose(), _matmul_mod).flatten().tolist()[0]
	return _cosineTheta


def randomGrouping(**kwargs):
	"""
	根据比例随机取得一数据表中的样本，样本不重复，严格按照截取比例随机选取。

	* 本函数输出形如，{'_input0_group1': Series(...), '_input0_group2': Series(...)}

	* _group1Percentage表示函数输出中，_input0_group1的数据占数据全体的比例

	:param _input0~n: dataframe, 需要进行分组的对象, 命名必须从_input0开始，如_input1， _input2...
	:param _group1Percentage: float, 0<分组比例<1, 建议不超过0.5, default, 0.5
	:return: None
	"""
	_input0 = kwargs['_input0']
	_group1Percentage = kwargs['_group1Percentage']
	if _group1Percentage <= 0 or _group1Percentage >= 1:
		warnings.warn('_group1Percentage不符合(0,1)定义域限制')
		exit(-1)
	_dataQuant = kwargs['_input0'].shape[0]
	_group1Quant = int(np.floor(_dataQuant * _group1Percentage))
	_locsPool = np.arange(_dataQuant).tolist()
	_group1Locs = []
	_output = {}

	while len(_group1Locs) < _group1Quant:
		_choosedLocsEachTime = np.unique(np.random.choice(_locsPool, _group1Quant)).tolist()
		_locsPool = list(set(_locsPool).difference(set(_choosedLocsEachTime)))
		_group1Locs = _group1Locs + _choosedLocsEachTime

	_choosedLocs = _group1Locs[0:_group1Quant]

	_group1_locs = list(sorted(_choosedLocs))
	_group2_locs = list(set(np.arange(_dataQuant).tolist()).difference(set(_group1_locs)))

	for i in range(len(kwargs.keys()) - 1):
		_keyName = '_input' + str(i)
		comStr = '_input' + str(i) + '_group1 = kwargs["' + _keyName + '"].iloc[_group1_locs, :]'
		exec(comStr)
		comStr = '_input' + str(i) + '_group2 = kwargs["' + _keyName + '"].iloc[_group2_locs, :]'
		exec(comStr)
		_outputCache = {'_input' + str(i) + '_group1': locals()['_input' + str(i) + '_group1'],
		                '_input' + str(i) + '_group2': locals()['_input' + str(i) + '_group2']}
		_output = {**_output, **_outputCache}
	return _output


def proportionalGrouping(**kwargs):
	"""
	根据比例间隔取得一数据表中的样本，样本不重复，严格按照截取比例间隔抽样选取。

	* 本函数输出形如，{'_input0_group1': Series(...), '_input0_group2': Series(...)}

	* _group1Percentage表示函数输出中，_input0_group1的数据占数据全体的比例

	:param _input0~n: dataframe, 需要进行分组的对象, 命名必须从_input0开始，如_input1， _input2...
	:param _group1Percentage: float, 0<分组比例<1, 建议不超过0.5, default, 0.5
	:return: None
	"""
	_input0 = kwargs['_input0']
	_group1Percentage = kwargs['_group1Percentage']
	if _group1Percentage <= 0 or _group1Percentage >= 1:
		warnings.warn('_group1Percentage不符合(0,1)定义域限制')
		exit(-1)
	_dataQuant = kwargs['_input0'].shape[0]
	_group1Quant = int(np.floor(_dataQuant * _group1Percentage))
	_eachLength = int(np.floor(1 / _group1Percentage))
	# 每次选取后向正方向取整
	_selectedLocs = []
	for i in range(_group1Quant):
		_selectedLoc_eachTime = int(np.ceil(((i * _eachLength) + ((i + 1) * _eachLength)) / 2))
		_selectedLocs.append(_selectedLoc_eachTime)
	# 选取的位置列表
	_group1_locs = _selectedLocs
	_group2_locs = list(set(np.arange(_dataQuant).tolist()).difference(set(_group1_locs)))
	# 输出
	_output = {}
	for i in range(len(kwargs.keys()) - 1):
		_keyName = '_input' + str(i)
		comStr = '_input' + str(i) + '_group1 = kwargs["' + _keyName + '"].iloc[_group1_locs, :]'
		exec(comStr)
		comStr = '_input' + str(i) + '_group2 = kwargs["' + _keyName + '"].iloc[_group2_locs, :]'
		exec(comStr)
		_outputCache = {'_input' + str(i) + '_group1': locals()['_input' + str(i) + '_group1'],
		                '_input' + str(i) + '_group2': locals()['_input' + str(i) + '_group2']}
		_output = {**_output, **_outputCache}
	return _output
