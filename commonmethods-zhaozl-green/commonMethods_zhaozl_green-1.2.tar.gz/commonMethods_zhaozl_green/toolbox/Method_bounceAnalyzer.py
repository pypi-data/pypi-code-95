"""
包括bounceAnalyzer

Classes
----------
bounceAnalyzer: 包括一种方法
    * updateAndDetermine: 对新传入的数据进行缓存记录，通过平均值计算等方法对跳变状态与持续跳变状态进行判断
        -- *逻辑描述见方法说明*

Example
----------
>>> from commonMethods_zhaozl.toolbox.Method_bounceAnalyzer import bounceAnalyzer

"""
import numpy as np  # 1.18.5


class bounceAnalyzer:
    """
    包括一种方法

    * updateAndDetermine: 对新传入的数据进行缓存记录，通过平均值计算等方法对跳变状态与持续跳变状态进行判断
        -- *逻辑描述见方法说明*

    [1] 参数
    ----------
    sampleRecorderSize:
        int, 对象所接收的传入数据的记录尺寸, optional, default 10
    determineThreshold:
        float, 新传入数据与本期数据进入前窗口（sampleRecorderSize）内数据均值的差值的报警限, optional, default 0.01
    bounceStatusRecorderSize:
        int, 最近是否发生跳变的状态记录的尺寸, optional, default 50
    keepBounceDetermineSize:
        int, 最近是否发生持续跳变的状态记录的尺寸,不可大于bounceStatusRecorderSize, :math:`this \\le\\ bounceStatusRecorderSize`, optional, default bounceStatusRecorderSize
    keepBounceDetermineThreshold:
        float, 当监测到窗口（keepBounceDetermineSize）内发生了跳变的情况的百分比, optional, default 0.4, 触发条件是：
            :math:`窗口内跳变发生次数 \\ge\\ 窗口内发生了跳变的情况的百分比 \\times\\ 最近是否发生跳变的状态记录的尺寸`

    [2] 方法
    ----------
    updateAndDetermine:
        对新传入的数据进行缓存记录，通过平均值计算等方法对跳变状态与持续跳变状态进行判断

    [3] 返回
    -------
    sampleRecorder:
        list, 对象所接收的传入数据的记录
    average_lastTime:
        float, 本期数据进入前窗口（sampleRecorderSize）内数据的均值
    average_thisTime:
        float, 本期数据进入后窗口（sampleRecorderSize）内数据的均值
    bounceStatus:
        0/1, 当期是否发生了数据跳变的判断结论, 1：发生 0：未发生
    bounceStatusRecorder:
        list[0/1], 最近窗口（bounceStatusRecorderSize）内是否发生跳变的状态记录
    keepBounceStatus:
        0/1, 最近是否发生持续跳变的判断结论, 1：发生 0：未发生

    [4] 示例1
    --------
    >>> status = []
    >>> bounceStatus = []
    >>> analyzerObj = bounceAnalyzer(_determineDistance=0.2)
    >>> for i in range(dataQuant):
    >>>     analyzerObj.updateAndDetermine(temper1[i])
    >>>     average_lastTime_all.append(analyzerObj.average_lastTime)
    >>>     status.append(analyzerObj.bounceStatus)
    >>>     bounceStatus.append(analyzerObj.keepBounceStatus)
    """

    def __init__(self, **kwargs):
        self.sampleRecorder = [0]
        self.sampleRecorderSize = 10 if '_sampleRecorderSize' not in kwargs.keys() else kwargs['_sampleRecorderSize']
        self.average_lastTime = []
        self.average_thisTime = []
        self.determineThreshold = 0.01 if '_determineThreshold' not in kwargs.keys() else kwargs['_determineThreshold']
        self.bounceStatus = []

        self.bounceStatusRecorder = []
        self.bounceStatusRecorderSize = 50 if '_bounceStatusRecorderSize' not in kwargs.keys() else kwargs['_bounceStatusRecorderSize']

        self.keepBounceDetermineSize = self.bounceStatusRecorderSize if '_bounceStatusRecorderSize' not in kwargs.keys() else kwargs['_bounceStatusRecorderSize']
        self.keepBounceDetermineThreshold = 0.4 if '_keepBounceDetermineThreshold' not in kwargs.keys() else kwargs['_keepBounceDetermineThreshold']
        self.keepBounceStatus = []

    def updateAndDetermine(self, _sampleCache):
        """
        对新传入的数据进行缓存记录，通过平均值计算等方法对跳变状态与持续跳变状态进行判断

        [1] 逻辑说明
        -----------
        输入一个测量值，对其进行滑动窗口的记录。计算记录该数据前后的窗口数据均值

        当输入测量值与记录该数据前窗口内数据均值的绝对值达到某一门限值时，触发【跳变】报警：
            :math:`|avg_lastTime - value_thisTime| \\ge\\ k_0`

        对是否跳变报警情况进行滑动窗口记录，并根据用以判断是否发生持续跳变的数据窗口尺寸取出近期数个判断结果

        当 *跳变发生率* 达到某一门限值时，触发【持续跳变】报警：
            :math:`ratio \\ge\\ k_1`

        [2] 参数
        --------
        _sampleCache:
            float, 新传入的数据
        """
        # 更新缓存记录
        self.average_lastTime = np.average(self.sampleRecorder)
        self.sampleRecorder.append(_sampleCache)
        if len(self.sampleRecorder) == self.sampleRecorderSize + 1:
            self.sampleRecorder.pop(0)
        self.average_thisTime = np.average(self.sampleRecorder)
        # 判断是否发生了跳变
        if np.abs(self.average_lastTime - _sampleCache) >= self.determineThreshold:
            self.bounceStatus = 1
        else:
            self.bounceStatus = 0
        # 判断是否发生了持续跳变
        self.bounceStatusRecorder.append(self.bounceStatus)
        if len(self.bounceStatusRecorder) == self.bounceStatusRecorderSize + 1:
            self.bounceStatusRecorder.pop(0)
        determineTargets = self.bounceStatusRecorder[-self.keepBounceDetermineSize:]
        bounceOccurredQuant = np.average(np.where(np.mat(determineTargets) == 0, 0, 1).flatten())
        self.keepBounceStatus = 1 if bounceOccurredQuant >= self.keepBounceDetermineThreshold else 0