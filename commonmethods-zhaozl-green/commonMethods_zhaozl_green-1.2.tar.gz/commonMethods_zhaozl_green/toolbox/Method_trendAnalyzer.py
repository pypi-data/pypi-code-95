"""
包括trendAnalyzer, trendPredict两个类

Classes
----------
* trendAnalyzer: 使用三阶滑动平均与一阶导对输入数据的快速/缓慢的上升/下降状态进行判断
    -- *逻辑描述见方法说明*

    ** plotDualYAxisFig: 在twinx中绘制数据与数据状态判断结果并选择性地填充状态区域的颜色

* trendPredict: 通过不断输入一时间序列的数值，顺序地对所定义窗口1内的数值进行三阶滑动平均处理，并计算所定义窗口2内的时序数据一阶导，通过对所定义窗口3内一阶导数据均值进行判断，以确定原始数据的上升/下降情况，包括：是否处理上升/下降状态，是否处于快速/慢速    变化状态

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_trendAnalyzer import trendAnalyzer

"""

import numpy as np  # 1.18.5
import pandas as pd  # 1.1.0
import matplotlib.pyplot as plt  # 3.3.0


class trendAnalyzer:
    """
    通过不断输入一时间序列的数值，顺序地对所定义窗口1内的数值进行三阶滑动平均处理，
    并计算所定义窗口2内的时序数据一阶导，通过对所定义窗口3内一阶导数据均值进行判断，
    以确定原始数据的上升/下降情况，包括：是否处理上升/下降状态，是否处于快速/慢速
    变化状态

    [1] 参数
    ----------
    smoothWindowSize:
        int, 进行窗口平滑处理的窗口尺寸, optional, default 30
    kValueWindowSize:
        int, 进行斜率计算单额窗口尺寸, 过大会导致判断滞后, 过小会导致各种状态快速变化, optional, default 130
    raiseThreshold:
        float, 用于判断数据上升状态的斜率阈值, 较大时表示判断结果为快速上升, optional, default 0.000001
    dropThreshold:
        float, 用于判断数据下降状态的斜率阈值, 较大时表示判断结果为快速下降, optional, default -0.000001

    [2] 方法
    ----------
    updateAndDetermine:
        用于新增数据并进行斜率的计算与判断
    plotDualYAxisFig:
        用于绘制原始数据及针对该数据的状态判断结果图形

    [3] 返回
    -------
    status:
        int, -1是下降状态, 1是上升状态, 0是平缓状态

    kValues:
        list, 斜率计算结果, kValues[-1]为当前斜率

    [4] 示例
    --------
    >>> res = []
    >>> analyzer = trendAnalyzer(smoothWindowSize=30, raiseThreshold=0.001, dropThreshold=-0.001)
    >>> for i in range(dataQuant):
    >>>     analyzer.update(data[i])
    >>>     res.append(analyzer.status)
    >>> analyzer.plotDualYAxisFig([data], res, -1)
    """

    def __init__(self, **kwargs):
        self.smoothWindowSize = 30 if 'smoothWindowSize' not in kwargs.keys() else kwargs['smoothWindowSize']
        self.kValueWindowSize = 130 if 'kValueWindowSize' not in kwargs.keys() else kwargs['kValueWindowSize']
        self.statusWindowSize = 200 if 'statusWindowSize' not in kwargs.keys() else kwargs['statusWindowSize']
        self.raiseThreshold = 0.000001 if 'raiseThreshold' not in kwargs.keys() else kwargs['raiseThreshold']
        self.dropThreshold = -0.000001 if 'dropThreshold' not in kwargs.keys() else kwargs['dropThreshold']
        self.__valueCheck()
        self.data = list([0] * self.smoothWindowSize)
        self.kValues = list([0] * self.kValueWindowSize)
        self.status = []
        self.statusRecords = list([0] * self.statusWindowSize)
        self.bounceStatus = []

    # 输入检查
    def __valueCheck(self):
        # 类型检查
        if not isinstance(self.smoothWindowSize, int):
            raise TypeError("smoothWindowSize 似乎不是int类型")
        if not isinstance(self.kValueWindowSize, int):
            raise TypeError("kValueWindowSize 似乎不是int类型")
        if not isinstance(self.raiseThreshold, float):
            raise TypeError("raiseThreshold 似乎不是float类型")
        if not isinstance(self.dropThreshold, float):
            raise TypeError("dropThreshold 似乎不是float类型")
        # 定义域检查
        if not self.raiseThreshold > 0:
            raise ValueError("raiseThreshold 应当为正数")
        if not self.dropThreshold < 0:
            raise ValueError("dropThreshold 应当为负数")

    # 插入数据并计算变化率
    def updateAndDetermine(self, _ele):
        """
        通过不断输入一时间序列的数值，顺序地对所定义窗口1内的数值进行三阶滑动平均处理，
        并计算所定义窗口2内的时序数据一阶导，通过对所定义窗口3内一阶导数据均值进行判断，
        以确定原始数据的上升/下降情况，包括：是否处理上升/下降状态，是否处于快速/慢速
        变化状态

        [1] 逻辑说明
        -----------
        输入一个测量数据，并对其进行记录，连续三次进行滑动平均，并计算其一阶导，将末端位置的数值作为数据当期的斜率进行记录

        当窗口内斜率的均值大于用于判断上升的斜率门限值时，判断为上升：
            :math:`kValues_avg > k_raise`

        当窗口内斜率的均值小于用于判断下降的斜率门限值时，判断为下降：
            :math:`kValues_avg < k_raise`

        否则，判断为无变化

        通过控制用于计算平均斜率的窗口尺寸，控制用于判断上升/下降的斜率，对【快速上升/快速下降】等状态进行表达


        [2] 参数
        ----------
        _ele:
            float, 新传入数据

        [3] 返回
        -------
        status:
            int, -1是下降状态, 1是上升状态, 0是平缓状态

        kValues:
            list, 斜率计算结果, kValues[-1]为当前斜率
        """

        def moveOneStep(_data, _newEle) -> list:
            _data.append(_newEle)
            _data.pop(0)
            return _data

        # 3阶平滑
        avgRecord_1st = moveOneStep(self.data, _ele)
        avgRecord_2st = moveOneStep(avgRecord_1st, np.average(avgRecord_1st))
        avgRecord_3st = moveOneStep(avgRecord_2st, np.average(avgRecord_2st))
        # 计算k值
        self.kValues = moveOneStep(self.kValues, np.diff(avgRecord_3st)[-1])
        # 判断k值是否为快速/平缓的上升/下降状态
        if np.average(self.kValues) > self.raiseThreshold:
            self.status = 1
        elif np.average(self.kValues) < self.dropThreshold:
            self.status = -1
        else:
            self.status = 0

    @staticmethod
    # 绘制单图
    def plotDualYAxisFig(_records: pd.DataFrame, _status: pd.DataFrame = None, **kwargs):
        """
        在twinx中绘制数据与数据状态判断结果并选择性地填充状态区域的颜色

        参数
        ----------

        _records:
            dataframe, 需要绘制在ax1的数据, columns将作为图例名称
        _status:
            dataframe, 需要绘制在ax2的数据, 一般是状态数据, 如-1 0 1等, columns将作为图例名称
        title:
            str, 图面名称, optional, default None
        ax1LegendLoc:
            str, 图面ax1图例位置, optional, default upper left
        ax2LegendLoc:
            str, 图面ax2图例位置, optional, default upper right
        fill:
            boolean, 是否做区域填充, optional, default False
        fillSec:
            list[int], 填充区域, optional, default [-1, 0, 1]
                当_status中的元素与此参数内各元素相同时，绘制该X轴区间范围内的Y∈[-1，1]的区域
        fillColor:
            list[str], 区域颜色, optional, default ['red', 'orange', 'green']
                使用该参数所规定的颜色绘制fillSec所规定的区域
        fillAlpha:
            list[float], 区域颜色透明度, optional, default [0.5， 0.5， 0.5]
        """
        title = None if '_title' not in kwargs.keys() else kwargs['_title']
        ax1LegendLoc = 'upper left' if '_ax1LegendLoc' not in kwargs.keys() else kwargs['_ax1LegendLoc']
        ax2LegendLoc = 'upper right' if '_ax2LegendLoc' not in kwargs.keys() else kwargs['_ax2LegendLoc']
        fill = False if '_fill' not in kwargs.keys() else True
        fillSec = [-1, 0, 1] if '_fillSec' not in kwargs.keys() else kwargs['_fillSec']
        fillColor = ['red', 'orange', 'green'] if '_fillColor' not in kwargs.keys() else kwargs['_fillColor']
        fillAlpha = [0.5, 0.5, 0.5] if '_fillAlpha' not in kwargs.keys() else kwargs['_fillAlpha']
        # 新建图面
        fig, ax1 = plt.subplots()
        plt.title(title)
        ax2 = ax1.twinx()
        # 参数解析
        _colName_records = _records.columns
        _colQuant_records = len(_colName_records.tolist())
        _colName_status = _status.columns
        _colQuant_status = len(_colName_status.tolist())
        _statusQuant = len(_status)
        # 绘制ax1图面
        ax1.plot(_records)
        ax1.legend(_colName_records, loc=ax1LegendLoc)
        # 绘制ax2图面
        ax2.plot(_status, ':')
        ax2.legend(_colName_status, loc=ax2LegendLoc)
        # 绘制区域填充
        if fill:
            y_neg1 = np.array([-1] * _statusQuant)
            y_0 = np.array([0] * _statusQuant)
            x = np.arange(0, _statusQuant, 1)
            y = np.array(_status.values.flatten().tolist())
            for i in range(len(fillSec)):
                status = np.array([fillSec[i]] * _statusQuant)
                ax2.fill_between(x, min(fillSec), max(fillSec), where=y==status, facecolor=fillColor[i], alpha=fillAlpha[i])
        else:
            pass
        plt.show()


class trendPredict:
    """
    使用三次指数平滑法根据前序数据对当前数据的预测值进行计算

    [1] 参数
    ----------
    _windowSize:
        int, 平滑处理的数据窗口尺寸, 不可大于7, 不可小于2, optional, default 5
    _smoothParam:
        float, 学习率, optional, default 0.9

    [2] 方法
    ----------
    varsInitiate:
        变量recorder, X, S1, S2, S3, P初始化
    update:
        读取并记录新数据
    trendPredict:
        通过近期数据对当前数据的预测值进行计算

    [3] 返回
    -------
    P:
        预测值, P[-1]有效
    [4] 示例1
    --------
    >>> pred = []
    >>> trendObj = trendPredict(_windowSize=5, _smoothParam=0.9)
    >>> recorder, X, S1, S2, S3, P = trendObj.varsInitiate()
    >>> for i in range(dataQuant):
    >>>     recorder = trendObj.update(_newData=data[i], _recorder=recorder)
    >>>     X, S1, S2, S3, P = trendObj.trendPredict(recorder, X, S1, S2, S3, P)
    >>>     pred.append(P[-1])
    """

    # ===== 属性初始化 ===== #
    def __init__(self, **kwargs):
        self.windowSize = 5 if '_windowSize' not in kwargs.keys() else kwargs['_windowSize']
        self.smoothParam = 0.9 if '_smoothParam' not in kwargs.keys() else kwargs['_smoothParam']
        self._recordShape = []
        self.lineRecord = []

    # ===== 变量初始化 ===== #
    def varsInitiate(self):
        self._recordShape = 10 - (self.windowSize - 1)  # 预测对象数据缓存量
        recorder = np.zeros(self._recordShape, dtype=float)
        X = np.zeros([self._recordShape, 1], dtype=float)
        S1 = np.zeros([2, 1], dtype=float)
        S2 = np.zeros([2, 1], dtype=float)
        S3 = np.zeros([2, 1], dtype=float)
        P = [0]*2
        return recorder, X, S1, S2, S3, P

    # ===== 数据记录 ===== #
    def update(self, _newData: float, _recorder: list) -> np.ndarray:
        """
        :param _newData: float, 新入库数据, 如46.3
        :param _recorder: list[float], 近期记录的数据, 如[0. 0. 0. 0. 0. 0.]
        :return: np.ndarray[float], 新入库后数据所组成的矩阵，如[[46.3], [46.3], [46.3], [46.3], [46.3], [46.3]]
        """
        if sum(_recorder) == 0:  # 如果_recorder是初始化的值，则将新入数据复制展开
            _lineRecord = np.reshape([_newData]*np.shape(_recorder)[0], (-1, 1))
        else:
            _lineRecord = np.concatenate((_recorder, np.mat(_newData)), 0)
        res = _lineRecord[-self._recordShape:, :]
        return res

    # ===== 趋势计算 ===== #
    def trendPredict(self, _recorder, _X, _S1, _S2, _S3, _P):
        """
        [1] 参数
        ----------
        _recorder:
            list[float], 近期记录的数据, 如[0. 0. 0. 0. 0. 0.]
        _P:
            list[float, float]， 预测值， _P[-1]根据前序数据对当期数据的预测值
        [2] 返回
        -------
        _P:
            list[float, float]， 预测值， _P[-1]根据前序数据对当期数据的预测值 \n
        _X, _S1, _S2, _S3:
            缓存量
        [3] 备注
        -----
        *  _X _S1 _S2 _S3 _P 是必要的缓存量
        """
        # ===== 平滑处理 ==== #
        for i in range(np.shape(_recorder)[0]):
            if i + self.windowSize <= np.shape(_recorder)[0]:
                _X[i, :] = np.mean(_recorder[i:i + self.windowSize, :], axis=0)
        _X = _X[0: np.shape(_recorder)[0] - (self.windowSize - 1), :]
        # ===== 检查S1 S2 S3 是否更新 ==== #
        if (_S1 == np.zeros_like(_S1)).all():
            _S1[0, :] = np.average(_X, axis=0)
            _S2[0, :] = np.average(_X, axis=0)
            _S3[0, :] = np.average(_X, axis=0)
        else:
            _S1 = np.concatenate((_S1, np.zeros((1, np.shape(_S1)[1]))))[-2:, :]
            _S2 = np.concatenate((_S2, np.zeros((1, np.shape(_S2)[1]))))[-2:, :]
            _S3 = np.concatenate((_S3, np.zeros((1, np.shape(_S3)[1]))))[-2:, :]
        # ===== 计算S1 S2 S3 ==== #
        S_1 = lambda a, X_t, S1_t_1: a * X_t + (1 - a) * S1_t_1
        S_2 = lambda a, S1_t, S2_t_1: a * S1_t + (1 - a) * S2_t_1
        S_3 = lambda a, S2_t, S3_t_1: a * S2_t + (1 - a) * S3_t_1
        for i in range(np.shape(_S1)[1]):
            _S1[-1, i] = S_1(self.smoothParam, _X[-1, i], _S1[0, i])
            _S2[-1, i] = S_2(self.smoothParam, _S1[-1, i], _S2[0, i])
            _S3[-1, i] = S_3(self.smoothParam, _S2[-1, i], _S3[0, i])
        # ===== 计算At Bt Ct ==== #
        A_t = lambda S1_t, S2_t, S3_t: 3 * S1_t - 3 * S2_t + S3_t
        B_t = lambda a, S1_t, S2_t, S3_t: a / (2 * (1 - a) ** 2) * (
                (6 - 5 * a) * S1_t - 2 * (5 - 4 * a) * S2_t + (4 - 3 * a) * S3_t)
        C_t = lambda a, S1_t, S2_t, S3_t: (a ** 2 / 2 / (1 - a) ** 2) * (S1_t - 2 * S2_t + S3_t)
        At = np.zeros((1, np.shape(_recorder)[1]))
        Bt = np.zeros((1, np.shape(_recorder)[1]))
        Ct = np.zeros((1, np.shape(_recorder)[1]))
        for i in range(np.shape(_S1)[1]):
            At[0, i] = A_t(_S1[-1, i], _S2[-1, i], _S3[-1, i])
            Bt[0, i] = B_t(self.smoothParam, _S1[-1, i], _S2[-1, i], _S3[-1, i])
            Ct[0, i] = C_t(self.smoothParam, _S1[-1, i], _S2[-1, i], _S3[-1, i])
        # ===== 计算P ==== #
        P_T = lambda at, bt, ct, T: at + bt * T + ct * T ** 2
        cacheP = []
        for i in range(np.shape(_S1)[1]):
            cacheP.append(P_T(At[0, i], Bt[0, i], Ct[0, i], 1))
        P = _P + cacheP
        return _X, _S1, _S2, _S3, P[-2:]
