"""
包括evennessDetermine一个类，modulo、angleCal两个函数

Classes
----------
evennessDetermine: 包括两种方法
    * compareWithOthersAverage, 同类测点温度值稳定，单一测点温度测量在正常范围内，但明显高于除本测点外的同类平均值
        -- *逻辑描述见方法说明*
    * circleSimilarity, 全体测点与均值圆的相似度, 使用向量间的相似度进行衡量
        -- *逻辑描述见方法说明*
其它：
    * modulo， 向量的模计算
    * angleCal， 向量间夹角余弦值计算

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_evennessDetermine import evennessDetermine

"""

import pandas as pd
import numpy as np

from pandas import DataFrame as DF


def modulo(_vector) -> float:
    """
    向量的模计算

    :param _vector: array, 向量, 可以使用numpy.array进行转化
    :return: 向量的模
    """
    return np.sqrt(_vector.dot(_vector))


def angleCal(_vector01, _vector02) -> float:
    """
    向量间夹角余弦值计算

    :param _vector01: array, 向量, 可以使用numpy.array进行转化
    :param _vector02: array, 向量, 可以使用numpy.array进行转化
    :return: 向量间夹角余弦值
    """
    return _vector01.dot(_vector02) / (modulo(_vector01) * modulo(_vector02))


class evennessDetermine:
    """
    包括两种方法：

    * compareWithOthersAverage, 同类测点温度值稳定，单一测点温度测量在正常范围内，但明显高于除本测点外的同类平均值
        -- *逻辑描述见方法说明*

    * circleSimilarity, 全体测点与均值圆的相似度, 使用向量间的相似度进行衡量
        -- *逻辑描述见方法说明*

    [1] 参数
    ----------
    thresholds:
        dataframe, 用于compareWithOthersAverage方法, 表示某测点当期数值与其它测点当期的均值之差不可大于每个元素, 必须项

    [2] 方法
    ----------
    compareWithOthersAverage: 同类测点温度值稳定，单一测点温度测量在正常范围内，但明显高于除本测点外的同类平均值

    circleSimilarity: 全体测点与均值圆的相似度, 使用向量间的相似度进行衡量

    [3] 示例1
    --------
    >>> thresholds = DF([[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]], columns=shortColumns)
    >>> evennessObj = evennessDetermine(_thresholds=thresholds)
    >>> similarityRecorder = []
    >>> determineResult = pd.DataFrame([])
    >>> for i in range(dataQuant):
    >>>     sample = DF([data.iloc[i].values], columns=shortColumns)
    >>>     evennessObj.compareWithOthersAverage(sample)
    >>>     evennessObj.circleSimilarity(_sample=sample)
    >>>     similarityRecorder.append(evennessObj.similarity)
    >>>     determineResult = pd.concat([determineResult, evennessObj.determineResult], axis=0)

    """

    def __init__(self, **kwargs):
        # compareWithOthersAverage 相关参数
        self.thresholds = kwargs['_thresholds']
        self.determineResult = []
        self.determineBasis = []
        # circleSimilarity 相关参数
        self.__cosineTheta__ = []
        self.__theta__ = []
        self.similarity = []

    def compareWithOthersAverage(self, _sample):
        """
        单一测点温度高于除本测点外的同类平均值

        [1] 逻辑说明
        -----------
        输入两个一维向量，分别代表当期对象测点数据和报警门限值

        针对某一维度数据 :math:`m_i` ，计算其它维度数据的当期均值 :math:`avg_i`

        若 :math:`a_i \\ge\\ avg_i + threshold_i` ，则触发报警

        [2] 参数
        ----------
        _sample:
            dataframe, 一组测点数据样本, 维度为1×N, 列名应当为测点名称

        [3] 返回
        -------
        determineResult:
            dataframe, 对输入的一维测点数据样本进行逻辑判断后的结果, 维度为1×N, 列名为测点名称

        determineBasis:
            dataframe, 对输入的一维测点数据样本进行逻辑判断后的依据（其它测点的当期均值）, 维度为1×N, 列名为测点名称
        """
        _sampleSum = np.sum(_sample.values, axis=1)
        _columns = _sample.columns
        _columnsQuant = len(_columns)
        _determineResult = []
        _determineBasis = []
        for i in range(_columnsQuant):
            _othersAverage = (_sampleSum - _sample.iloc[0, i]) / (_columnsQuant - 1)
            if _sample.iloc[0, i] >= self.thresholds.iloc[0, i] + _othersAverage:
                _determineResult.append(1)
                _determineBasis.append(np.around(_othersAverage[0], 1))
            else:
                _determineResult.append(0)
                _determineBasis.append(np.around(_othersAverage[0], 1))
        self.determineResult = DF([_determineResult], columns=_columns)
        self.determineBasis = DF([_determineBasis], columns=_columns)

    # 全体测点与均值圆的相似度
    def circleSimilarity(self, _sample):
        """
        全体测点与均值圆的相似度, 使用向量间的相似度进行衡量

        [1] 逻辑说明
        -----------
        输入一个一维向量，代表当期对象测点数据

        针对当期输入数据所构成的向量 :math:`\\vec{x}` ，计算其它维度数据的当期均值 :math:`s` ，以构建出一个以该均值为半径的正多边形，并以向量 :math:`\\vec{s}` 表示

        通过计算 :math:`\\vec{x}` 与 :math:`\\vec{s}` 两向量间的夹角余弦，以表示输入向量与均值向量间的相似度，或用以表示‘圆度’

        [2] 参数
        ----------
        _sample:
            dataframe, 一组测点数据样本, 维度为1×N, 列名应当为测点名称

        [3] 返回
        -------
        similarity:
            float, 对输入的一维测点数据样本进行计算后的相似度（夹角余弦）

        __cosineTheta__:
            float, 与similarity属性一致

        __theta__:
            float, 向量间夹角
        """
        _sampleAvg = np.average(_sample.values)
        _sampleSize = np.shape(_sample.values)[1]
        _sampleVector = np.asarray(_sample.values[0])
        _standardVector = np.asarray([_sampleAvg]*_sampleSize)
        self.__cosineTheta__ = angleCal(_sampleVector, _standardVector)
        self.__theta__ = np.arccos(self.__cosineTheta__)
        self.similarity = self.__cosineTheta__
