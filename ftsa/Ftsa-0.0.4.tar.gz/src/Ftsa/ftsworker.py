#!/usr/bin/python3.7 
# -*- coding: utf-8 -*-

"""
配置数据源相关信息，获取金融时间序列数据
"""
import time
import pandas as pd
import math
import numpy as np
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt

class worker(object):

    def __init__(self, csv_path=None, labels=None):
        # 初始化
        self.csv_path = csv_path
        self.t = labels['time']
        self.v = labels['val']
    
    def load(self):
        # 读取数据并返回
        t0 = time.time()
        data = pd.read_csv(self.csv_path)
        t1 = time.time()
        print('* Data loaded. %.2fs' % (t1-t0))
        data = data[[self.t, self.v]]
        return data


    def sign(self, x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0
    
    def find_changepoints(self, s, h):
        # 对指定序列寻找变点的方法

        v = self.v

        # 该序列的起始位置
        pad = s.index[0]
        
        # 变点位置序列
        b = [0]
        # 变点值序列
        c = [s[v].iloc[0]]

        # 游标
        i = 0
        k = i
        # 输入序列长度s
        n = len(s)-1

        # 第一步
        # region中的趋势，初始为0
        r = 0
        # 滑动游标
        i = min(i+h, n)
        ss = ( s[v].iloc[k] - s[v].iloc[i] ) / float( k - i )
        # 更新变化趋势
        r = self.sign(ss)
        
        while r == 0 and i < n:
            # 若第一段趋势为0，则补充更多数据
            i = min(i+h, n)
            ss = ( s[v].iloc[k] - s[v].iloc[i] ) / float( k - i )
            # 更新变化趋势
            r = self.sign(ss)        

        # 第二步开始
        j = i
        while j < n:
            # 设置一个标记，表示下一段趋势是否和前一段趋势相同
            sig = 1
            while sig > 0:
                k = min(i+h, n)
                if k == i:
                    break
                else:
                    ss = ( s[v].iloc[k] - s[v].iloc[j] ) / float( k - j )
                    if self.sign(ss) == r:
                        # 趋势相同，则继续考察下一段
                        sig = 1
                        j = k
                        i = j
                    else:
                        # 趋势不同，则跳到寻找变点
                        sig = -1
                    
            # 抽取当前考察的时间窗口
            window = s[v].iloc[j : min(j+h, n)+1] * r
            
            # 如果该区间上时间序列为常数，即没有任何变化，那么把变点标记为区间末端
            if window.max() == window.min():
                j_max = min(j+h, n)
            # 否则寻找使r*ss最大的点
            else:
                j_max = window.idxmax()-pad
            
            # 记录增加的变点
            if j_max != b[-1]:
                b.append(j_max)
                c.append(s[v].iloc[j_max])

            # 移动游标
            j = j_max
            i = j
            # 更新趋势
            r = -r
            
        # 返回：b为变点集合，c为对应值的集合
        return [b, c]


    def get_rv(self, s):
        # 对任意一个输入的序列，计算已实现波动率
        rv = 0
        for i in range(0, len(s)-1):
            rv = rv + (math.log(s[i+1]) - math.log(s[i]))**2
        return rv
    
    def rv_changepoints(self, b, s):
        # 输入变点序列、原始序列，计算每个区间的已实现波动率
        v = self.v
        rvps = []
        for i in range(0, len(b)-1):
            ss = s[v].iloc[b[i] : b[i+1]]
            # 该区间上的已实现波动率
            rv = self.get_rv(ss.tolist())
            rvps.append(rv)
        return rvps

    def distance(self, x, y):
        return abs(x-y)
    
    def dtw(self, X,Y):
        # 输入两个序列X和Y，计算其DTW距离
        l1 = len(X)
        l2 = len(Y) 
        
        # X和Y所有元素的两两距离矩阵
        M = []
        for i in range(0, l1):
            row = []
            for j in range(0, l2):
                row.append(self.distance(X[i],Y[j]))
            M.append(row)

        # 矩阵D用于记录动态规划距离
        D = []
        for i in range(0, l1+1):
            row = []
            for j in range(0, l2+1):
                row.append(0)
            D.append(row)
        
        # 初始化矩阵D
        D[0][0] = 0 
        for i in range(1, l1+1):
            D[i][0] = 999999
        for j in range(1, l2+1):
            D[0][j] = 999999
        
        for i in range(1, l1+1):
            for j in range(1, l2+1):
                # 根据动态规划选择从i-1,j-1到i,j的最短连接，并累加DTW距离
                D[i][j] = M[i-1][j-1] + min(D[i-1][j], D[i][j-1], D[i-1][j-1])
        # 动态规划距离矩阵的最后一个元素即最终DTW距离
        echo = D[-1][-1]
        return echo

    def cluster(self, df, K=2, rv_K=2, mop=1, op=0, h=5):
        # 基于dtw距离进行聚类
        """
        定义超参数
        """
        # 平滑窗口
        #h = 5
        # 指定对变点序列聚为K类
        #K = 2
        # 聚类参数-簇间距离度量方式
        method = 'complete'
        # 关于rv的聚类参数
        #rv_K = 2
        # 是否绘图，op=1表示绘图
        #op = 1
        # 是否进行两阶段聚类，op=1表示是
        #mop = 1

        font2 = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 20,
        }

        t = self.t
        v = self.v

        # 聚类-第1步：将原始数据切分成个单日的时间序列样本
        t0 = time.time()
        samples = []
        names = {}
        name_cnt = 0
        for i in range(0, len(df), 48):
            temp_sample = df.iloc[i : i+48]
            samples.append(temp_sample)
            names[name_cnt] = df.iloc[i][t]
            name_cnt = name_cnt + 1
        t1 = time.time()
        print("*** Step 1: Slicing finished. %d series generated. (%.2fs)" % (len(samples), t1-t0))
            
        # 聚类-第2步：对所有样本，抽取变点序列，及已实现波动率序列
        t0 = time.time()
        point_series = []
        point_v_series = []
        rv_series = []
        for i in range(0, len(samples)):
            # 抽取变点
            [b, c] = self.find_changepoints(samples[i], h)
            point_series.append(b)
            point_v_series.append(c)

            if mop == 1:
                # 抽取已实现波动率序列
                rvps = self.rv_changepoints(b, samples[i])  
                rv_series.append(rvps)
        t1 = time.time()    
        
        if mop == 1:
            print("*** Step 2: Finding changepoints as well as RV series finished. %d series generated. (%.2fs)" % (len(point_series), t1-t0))
        else:
            print("*** Step 2: Finding changepoints finished. %d series generated. (%.2fs)" % (len(point_series), t1-t0))

        # 聚类-第3步：计算所有【变点】序列之间，两两DTW矩阵
        t0 = time.time()
        n = len(point_v_series)
        DTW = np.zeros([n, n])
        for i in range(0, n):
            for j in range(i, n):
                temp_dtw = self.dtw(point_v_series[i], point_v_series[j])
                DTW[i][j] = temp_dtw
                DTW[j][i] = temp_dtw
        t1 = time.time()
        print("*** Step 3: DTW matrix computation finished. (%.2fs)" % (t1-t0))

        # 聚类-第4步：根据【变点】DTW矩阵，层次聚类
        t0 = time.time()
        # 进行层次聚类
        Z = sch.linkage(DTW, method=method) 

        if op == 1:
            # 画图-展示层次聚类图
            plt.figure(figsize=(10,5))
            P = sch.dendrogram(Z, labels=range(n))
            plt.plot()
            plt.title("Dendrogram of changepoint series")
            plt.savefig('dendrogram.png')
            plt.close()

        cluster_res = sch.fcluster(Z, t=K, criterion='maxclust') 
        t1 = time.time()
        print("*** Step 4: Clustering-changepoints finished. (%.2fs)" % (t1-t0))
        print(cluster_res)

        # 根据聚类结果，将样本分配到不同簇对应的列表中
        [cluster_samples, label] = self.assign(samples, cluster_res, K)

        if mop == 0:
            # 若无需进行2阶段聚类，则直接返回当前聚类结果
            name_label = {}
            for d, x in label.items():
                name_label['changepoint cluster %d' % d] = []
                for _x in x:
                    name_label['changepoint cluster %d' % d].append(names[_x])
            return name_label
        else:
            # 若需要进行2阶段聚类
            name_label_s2 = {}

            # 先根据第一阶段聚类结果划分样本
            [point_v_series_res, label] = self.assign(point_v_series, cluster_res, K)
            [cluster_rvs, label] = self.assign(rv_series, cluster_res, K)

            for k in range(1, K+1):
                # 对每个簇，内部根据RV进行层次聚类
                temp_cluster = cluster_rvs[k]
                temp_cluster_series = point_v_series_res[k]
                temp_label = label[k]

                # 记录对应的日期名
                temp_names = {}
                for i in range(len(temp_label)):
                    temp_names[i] = names[temp_label[i]]

                # 对样本量很少的簇，不再分类
                if len(temp_cluster) > 10:
                    _t0 = time.time()
                    # 计算基于RV的DTW距离矩阵
                    n = len(temp_cluster)
                    DRV = np.zeros([n, n])
                    for i in range(0, n):
                        for j in range(i, n):
                            temp_dtw = self.dtw(temp_cluster[i], temp_cluster[j])
                            DRV[i][j] = temp_dtw
                            DRV[j][i] = temp_dtw
                    _t1 = time.time()    
                    
                    print("* Step 5. Cluster-%d Distance Matrix computation finished. (%.2fs)" % (k, _t1-_t0))

                    # 层次聚类
                    rv_Z = sch.linkage(DRV, method=method) 
         
                    if op == 1:
                        # 显示聚类树状图
                        plt.figure(figsize=(10,5))
                        P = sch.dendrogram(rv_Z)
                        plt.plot()
                        plt.title("Dendrogram of RV series in Cluster %d" % (k+1))
                        plt.savefig('dendrogram_rv_%d.png' % (k+1))
                        plt.close()

                    # 指定聚为rv_K类
                    rv_cluster_res = sch.fcluster(rv_Z, t=rv_K, criterion='maxclust') 
                    #print len(rv_cluster_res)
                    [rv_cluster_rvs, rv_label] = self.assign(temp_cluster, rv_cluster_res, rv_K)
                    [rv_cluster_rvs_series, rv_label] = self.assign(temp_cluster_series, rv_cluster_res, rv_K)

                    rv_name_label = {}
                    for d, x in rv_label.items():
                        rv_name_label['RV cluster %d' % d] = []
                        for _x in x:
                            rv_name_label['RV cluster %d' % d].append(temp_names[_x])
                    name_label_s2['changepoint cluster %d' % k] = rv_name_label
            return name_label_s2
                    

    
    def assign(self, samples, cluster_res, K):
        # 输入聚类结果，将原样本集合划分为不同簇的集合
        # 先准备K个空列表，用于对每个簇，存放对应的样本
        res = {}
        # 保存各个簇中样本序列的序号
        label = {}
        for i in range(1, K+1):
            res[i] = []
            label[i] = []
        # 根据聚类结果，将样本分配到不同簇对应的列表中
        for i in range(0, len(samples)):
            res[cluster_res[i]].append(samples[i])
            label[cluster_res[i]].append(i)
        return [res, label]
