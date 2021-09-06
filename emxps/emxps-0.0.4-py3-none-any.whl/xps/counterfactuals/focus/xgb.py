from collections import namedtuple
import pandas as pd
import numpy as np

SKLTree = namedtuple('SKLTree', [
    'children_left',
    'children_right',
    'feature',
    'threshold',
    'value',
    'node_count',
])

SKLDecisionTree = namedtuple('SKLDecisionTree', [
    'classes_',
    'tree_',
])

SKLEnsemble = namedtuple('SKLEnsemble', [
    'estimators_',
    'classes_',
])


def booster_to_skl_ensemble(booster, nb_outputs=1, nb_classes=2):
    df = booster.trees_to_dataframe()

    def id_to_node(x):
        if pd.isnull(x):
            return -1
        else:
            return int(x.split('-')[1])

    def fid_to_f(x):
        if x == 'Leaf':
            return -2
        else:
            if booster.feature_names is None:
                return int(x[1:])
            else:
                return np.argwhere(np.array(booster.feature_names) == x).flatten()[0]

    def split_to_threshold(x):
        if pd.isnull(x):
            return -2
        else:
            return x

    def df_to_values(df):
        return (
            df['Gain'] *
            np.ma.masked_where((df['Feature'] != 'Leaf').values, np.ones(len(df), dtype=float)).filled(np.nan)
        ).values

    def df_to_skltree(df):
        return SKLDecisionTree(
            tree_=SKLTree(
                node_count=df['Node'].max() + 1,
                children_left=df['Yes'].apply(id_to_node).values,
                children_right=df['No'].apply(id_to_node).values,
                feature=df['Feature'].apply(fid_to_f).values,
                threshold=df['Split'].apply(split_to_threshold).values,
                value=df_to_values(df),
            ),
            classes_=np.arange(nb_classes),
        )

    return SKLEnsemble(
        estimators_=[df_to_skltree(df[df['Tree'] == t]) for t in range(df['Tree'].max() + 1)],
        classes_=np.arange(nb_classes),
    )
