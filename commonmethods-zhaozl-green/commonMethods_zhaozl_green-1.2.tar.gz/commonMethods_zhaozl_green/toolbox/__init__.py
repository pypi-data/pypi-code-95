"""
Classes
----------
* timeTrans: 通过输入list(int)或者int形式的时间戳unixTimestamp，与形如'%Y/%m/%d %H:%M:%S'的formation，对时间戳进行计算并输出string

* mysqlOperator: mysql数据库操作， 包括创建table、添加列、新增数据、更新数据、查询数据

* comtradeParser: 通过输入符合comtrade规范的文件名，对数据内容进行输出

* processBar: 在打印的循环体中输出进度条

* trendAnalyzer:

	** trendAnalyzer: 使用三阶滑动平均与一阶导对输入数据的快速/缓慢的上升/下降状态进行判断

	** trendPredict: 通过不断输入一时间序列的数值，顺序地对所定义窗口1内的数值进行三阶滑动平均处理，并计算所定义窗口2内的时序数据一阶导，通过对所定义窗口3内一阶导数据均值进行判断，以确定原始数据的上升/下降情况，包括：是否处理上升/下降状态，是否处于快速/慢速变化状态
	
* bounceAnalyzer: 对新传入的数据进行缓存记录，通过平均值计算等方法对跳变状态与持续跳变状态进行判断

* evennessDetermine: 包括两种方法

	** compareWithOthersAverage, 同类测点温度值稳定，单一测点温度测量在正常范围内，但明显高于除本测点外的同类平均值

	** circleSimilarity, 全体测点与均值圆的相似度, 使用向量间的相似度进行衡量

	** modulo， 向量的模计算

	** angleCal， 向量间夹角余弦值计算

"""

from . import *