# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 16:54:05 2021
@author: wll
"""

import time
from scipy.spatial import ConvexHull
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # 空间三维画图
import numpy
from sklearn.metrics import f1_score, accuracy_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer


def timmer(func):
    def deco(*args, **kwargs):
        start_time = time.time()
        print(f'\n{time.strftime("%H:%M:%S", time.localtime())} {func.__name__} start running ...')
        res = func(*args, **kwargs)
        end_time = time.time()
        print(f'{time.strftime("%H:%M:%S", time.localtime())} {func.__name__} costed {(end_time-start_time):.2f} Sec')
        return res
    return deco


def plot3Dscatter(data_df, isPlotConvexhull=True, labelValues='all'):
    """
    data_df : pandas DataFrame.
        The first three columns are X,Y,Z and the fourth column is label
    """
    if labelValues == 'all':
        labelValues = set(data_df.iloc[:, -1])
    colors = [plt.cm.tab10(i/float(len(labelValues)-1)) for i in range(len(labelValues))]
    fig = plt.figure(figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')  # 分辨率，背景颜色，边缘颜色
    ax = Axes3D(fig)
    for i, v in enumerate(labelValues):
        points_df = data_df[data_df.iloc[:, -1] == v]
        plt.plot(points_df.iloc[:, 0], points_df.iloc[:, 1], points_df.iloc[:, 2], 'o', c=colors[i], label=str(v))  # ,
        plt.legend()
        # plt.
        if isPlotConvexhull:
            points = points_df.iloc[:, :3].values
            hull = ConvexHull(points)
            for simplex in hull.simplices:
                plt.plot(points[simplex, 0], points[simplex, 1], points[simplex, 2], c=colors[i])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.show()


def plot2Dscatter(data_df, isPlotConvexhull=True, labelValues='all'):
    """
    data_df : pandas DataFrame.
        The first three columns are X,Y,Z and the fourth column is label
    """
    if labelValues == 'all':
        labelValues = set(data_df.iloc[:, -1])
    colors = [plt.cm.tab10(i/float(len(labelValues)-1)) for i in range(len(labelValues))]
    # fig = plt.figure(figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')  # 分辨率，背景颜色，边缘颜色
    for i, v in enumerate(labelValues):
        points_df = data_df[data_df.iloc[:, -1] == v]
        plt.plot(points_df.iloc[:, 0], points_df.iloc[:, 1], 'o', c=colors[i], label=v)  # ,
        plt.legend()
        if isPlotConvexhull:
            points = points_df.iloc[:, :2].values
            hull = ConvexHull(points)
            for simplex in hull.simplices:
                plt.plot(points[simplex, 0], points[simplex, 1], c=colors[i])  # , points0[simplex, 2]


# # from shenweichen
class TopKRanker(OneVsRestClassifier):
    def predict(self, X, top_k_list):
        probs = numpy.asarray(super(TopKRanker, self).predict_proba(X))
        all_labels = []
        for i, k in enumerate(top_k_list):
            probs_ = probs[i, :]
            labels = self.classes_[probs_.argsort()[-k:]].tolist()
            probs_[:] = 0
            probs_[labels] = 1
            all_labels.append(probs_)
        return numpy.asarray(all_labels)


class Classifier(object):

    def __init__(self, embeddings, clf):
        self.embeddings = embeddings
        self.clf = TopKRanker(clf)
        self.binarizer = MultiLabelBinarizer(sparse_output=True)

    def train(self, X, Y, Y_all):
        self.binarizer.fit(Y_all)
        X_train = [self.embeddings[x] for x in X]
        Y = self.binarizer.transform(Y)
        self.clf.fit(X_train, Y)

    def evaluate(self, X, Y):
        top_k_list = [len(y) for y in Y]
        Y_ = self.predict(X, top_k_list)
        Y = self.binarizer.transform(Y)
        averages = ["micro", "macro", "samples", "weighted"]
        results = {}
        for average in averages:
            results[average] = f1_score(Y, Y_, average=average)
        results['acc'] = accuracy_score(Y, Y_)
        print('-------------------')
        print(results)
        return results
        print('-------------------')

    def predict(self, X, top_k_list):
        X_ = numpy.asarray([self.embeddings[x] for x in X])
        Y = self.clf.predict(X_, top_k_list=top_k_list)
        return Y

    def split_train_evaluate(self, X, Y, train_precent, seed=0):
        state = numpy.random.get_state()

        training_size = int(train_precent * len(X))
        numpy.random.seed(seed)
        shuffle_indices = numpy.random.permutation(numpy.arange(len(X)))
        X_train = [X[shuffle_indices[i]] for i in range(training_size)]
        Y_train = [Y[shuffle_indices[i]] for i in range(training_size)]
        X_test = [X[shuffle_indices[i]] for i in range(training_size, len(X))]
        Y_test = [Y[shuffle_indices[i]] for i in range(training_size, len(X))]

        self.train(X_train, Y_train, Y)
        numpy.random.set_state(state)
        return self.evaluate(X_test, Y_test)


if __name__ == '__main__':
    points0_df = pd.DataFrame(np.random.randn(500, 3))
    points0_df['label'] = 0
    points1_df = pd.DataFrame(np.random.randn(500, 3)+3)
    points1_df['label'] = 1
    points2_df = pd.DataFrame(np.random.randn(500, 3)-3)
    points2_df['label'] = 2
    data_df = pd.concat([points0_df, points1_df, points2_df], axis=0, ignore_index=True)
    plot3Dscatter(data_df, isPlotConvexhull=1)
    plot2Dscatter(data_df, isPlotConvexhull=1)
    # em = pd.read_csv('emb2d.csv')
    # labels = pd.read_csv('lables.csv')
    # data_df = pd.DataFrame(em)
    # data_df['label'] = labels
    # em3 = pd.read_csv('emb3d.csv')
    # data_df3 = pd.DataFrame(em3)
    # data_df3['label'] = labels
    # plot3Dscatter(data_df3, isPlotConvexhull=0, labelValues=[4,11])
    # plot2Dscatter(data_df, isPlotConvexhull=0)
