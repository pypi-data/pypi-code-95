import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict, Counter
import logging

from emutils.utils import get_leaves
from emutils.utils import display

import plotly.express as px


# %%
def join_df_by_features_names(df, features):
    def transform_feature_names(df):
        if np.all([fname.startswith('f') or fname == 'Leaf' for fname in df['Feature']]):
            df['Feature'] = df['Feature'].apply(
                lambda x: features.iloc[int(x[1:])]['Feature'] if x.startswith('f') else x
            )
        return df

    features_temp = features.copy()
    features_temp['#'] = features_temp.index.values
    features_temp.set_index('Feature', inplace=True)
    if "Feature" not in df.columns.values:  # If Feature is the index
        df['Feature'] = df.index.values
        # Transfrom f1, f2, ... to features names
        df = transform_feature_names(df)
        df = df.join(features_temp, on='Feature', how='left')
        df.set_index('#', inplace=True)
        df.sort_index(inplace=True)
    else:
        df = transform_feature_names(df)
        df = df.join(features_temp, on='Feature', how='left')
    return df


scores = {
    "weight": "the number of times a feature is used to split the data across all nodes",
    "gain": "the average gain across all splits the feature is used in",
    "cover": "the average (samples) coverage across all splits the feature is used in",
    "total_gain": "the total gain across all splits the feature is used in",
    "total_cover": "the total (samples) coverage across all splits the feature is used in"
}


def get_feature_importance(booster, features=None, plot=False):
    """
        Extract all the importance measures from the XGBoost Model
    """
    # Extract importances from the booster
    importance = pd.concat(
        [
            pd.DataFrame(
                [list(i) for i in booster.get_score(importance_type=importance_type).items()],
                columns=['feature', importance_type]
            ).set_index('feature') for importance_type in scores.keys()
        ],
        axis=1
    )

    # Round stuff to make it presentable in PlotLy
    importance = importance.apply(lambda s: s.apply(lambda x: round(x, 1)))

    # Create also percentage for ease of comparison
    for col in importance:
        importance[col + "_perc"] = (importance[col] / importance[col].max() *
                                     100).apply(lambda x: str(round(x, 2)) + '%')

    return importance


def is_f_feature(x):
    if not x.startswith('f'):
        return False
    try:
        int(x[1:])
    except:
        return False
    return True


def compute_nodes_depth(nodes, G):
    # Compute node depth
    def get_node_depth(T, node):
        t, _ = [int(v) for v in node.split('-')]
        root = f"{t}-0"
        return nx.algorithms.shortest_path_length(T, root, node)

    depth = pd.DataFrame()
    depth['Depth'] = nodes['ID'].apply(lambda x: get_node_depth(G, x))
    depth['Shallowness'] = depth['Depth'].max() - depth['Depth']
    return depth


def get_graphs(nodes, features):

    nodes = nodes.copy()

    def to_feature_index(x):
        if x == 'Leaf':
            return x
        elif is_f_feature(x):
            return int(x[1:])
        else:
            indexes = np.argwhere(x == features).flatten()
            if len(indexes) == 1:
                return indexes[0]
            else:
                raise ValueError('Feature name not found!')

    def to_feature_names(x):
        return np.array(features)[int(x)] if x != 'Leaf' else x

    # Convert the features names to indexes
    nodes['Feature'] = nodes['Feature'].apply(to_feature_index)
    nodes['#'] = nodes['Feature'].copy()

    # And to names
    nodes['Feature'] = nodes['Feature'].apply(to_feature_names)

    nb_trees = len(nodes['Tree'].unique())

    logging.info(f'The model has {len(nodes)} nodes.')
    logging.info(f'The model has {nb_trees} trees.')
    logging.info(f'Therefore each tree has on average {len(nodes)/nb_trees} nodes.')

    # Let's put them in a directed graph
    G = nx.DiGraph()  # Whole model
    Ts = defaultdict(nx.DiGraph)  # Individual trees

    for _, row in nodes.iterrows():
        for child in [row['Yes'], row['No']]:
            if isinstance(child, str):
                Ts[row['Tree']].add_edge(row['ID'], child)
                G.add_edge(row['ID'], child)

    for row in nodes.to_dict('records'):
        G.add_node(row['ID'], **row)
        Ts[row['Tree']].add_node(row['ID'], **row)

    # Transform to list (sorted by tree)
    assert len(Ts) == nb_trees
    Ts = [Ts[i] for i in range(nb_trees)]

    # Assert that first node is the root in all trees
    assert np.all(np.array([list(T.nodes.values())[0]['Node'] for T in Ts]) == 0)

    return G, Ts


def get_tree_stats(nodes, Ts):
    # Extract some statistics for the trees
    trees = pd.DataFrame()
    trees['Depth'] = [nx.algorithms.dag.dag_longest_path_length(Ts[i]) for i in range(len(Ts))]
    trees['Width'] = list(Counter(nodes[nodes['Feature'] == 'Leaf']['Tree'].values).values())
    trees['#Nodes'] = [len(T.nodes) for T in Ts]
    trees['#Leaves (Paths)'] = [len(list(get_leaves(T))) for T in Ts]

    return trees


def compute_features_depth(nodes, features, G):
    nodes = nodes.copy()

    nodes = pd.concat([nodes, compute_nodes_depth(nodes, G)], axis=1)

    def to_feature_index(x):
        if x == 'Leaf':
            return x
        elif is_f_feature(x):
            return int(x[1:])
        elif features is not None:
            indexes = np.argwhere(x == features).flatten()
            if len(indexes) == 1:
                return indexes[0]
            else:
                raise ValueError('Feature name not found!')
        else:
            raise ValueError('Features have names but not array with features names was passed.')

    # Convert the features names to indexes
    nodes['Feature'] = nodes['Feature'].apply(to_feature_index)

    nodes = nodes[nodes['Feature'] != 'Leaf']

    depth = pd.DataFrame()
    depth['Depth'] = nodes.groupby('Feature').mean().sort_index()['Depth']
    depth['Shallowness'] = nodes.groupby('Feature').mean().sort_index()['Shallowness']
    depth['Shallowness STD'] = nodes.groupby('Feature').std().sort_index()['Shallowness']
    return depth


def get_feature_splits(
    nodes,
    nb_features=None,
    features=None,
):
    if features is None and nb_features is None:
        raise ValueError('Must pass features or nb_features.')

    if features is not None:
        features = np.array(features)
        if nb_features is not None:
            assert len(features) == nb_features
        else:
            nb_features = len(features)

    nodes = nodes.copy()

    def to_feature_index(x):
        if x == 'Leaf':
            return x
        elif is_f_feature(x):
            return int(x[1:])
        elif features is not None:
            indexes = np.argwhere(x == features).flatten()
            if len(indexes) == 1:
                return indexes[0]
            else:
                raise ValueError('Feature name not found!')
        else:
            raise ValueError('Features have names but not array with features names was passed.')

    # Convert the features names to indexes
    nodes['Feature'] = nodes['Feature'].apply(to_feature_index)

    # Get all the split values for each of the features
    splits = defaultdict(list)
    for _, row in nodes.iterrows():
        if not np.isnan(row['Split']):  # If it's not a leaf
            splits[int(row['Feature'])].append(row['Split'])

    assert len(splits) <= nb_features
    splits = [list(np.unique(np.array(sorted(splits[k])))) for k in range(nb_features)]

    # Not interesting
    #     splits_stats = pd.DataFrame(
    #         [pd.DataFrame(vs).describe().T.to_dict("records")[0] if len(vs) > 0 else {} for vs in splits]
    #     )
    #     return splits, stats
    return splits


def __splits_to_values(splits, how: str, eps: float):
    if len(splits) == 0:
        return [0]

    if how == 'left':
        return ([splits[0] - eps] + [(splits[i] + eps) for i in range(len(splits) - 1)] + [splits[-1] + eps])
    elif how == 'right':
        return ([splits[0] - eps] + [(splits[i + 1] - eps) for i in range(len(splits) - 1)] + [splits[-1] + eps])
    elif how == 'center':
        return (
            [splits[0] - eps] + [(splits[i] + splits[i + 1]) / 2 for i in range(len(splits) - 1)] + [splits[-1] + eps]
        )
    else:
        raise ValueError('Invalid mode.')


def splits_to_values(splits, how: str, eps=1e-6):
    return [np.unique(np.array(__splits_to_values(s, how=how, eps=eps))) for s in splits]


# def get_feature_values(splits):
#     # Transform splits in values (take avg and -1/+1)
#     def splits_to_values(s):
#         if len(s) == 0:
#             logging.warning("This feature do not have any splits, using 0.")
#             return [0]
#         else:
#             return (
#                 [s[0] - np.finfo(type(s[0])).eps] + [(s[i] + s[i + 1]) / 2
#                                                      for i in range(len(s) - 1)] + [s[-1] + np.finfo(type(s[-1])).eps]
#             )

#     feature_values = [splits_to_values(s) for s in splits]

#     # Let's get stats
#     feature_values_stats = pd.DataFrame(
#         {k: pd.DataFrame(vs).describe().T.to_dict("records")[0]
#          for k, vs in enumerate(feature_values)}
#     ).T

#     # Let's check the number of naive combinations (huge of course)
#     naive_combs = prod(feature_values_stats['count'].values)
#     print(f'The naive discrete space induced by tree splits has size {naive_combs}')

#     # Return
#     return feature_values


def tree_predict(T, x):
    curnode = list(T.nodes.values())[0]
    while not np.isnan(curnode['Split']):
        if x[int(curnode['#'])] < curnode['Split']:
            curnode = T.nodes[curnode['Yes']]
        else:
            curnode = T.nodes[curnode['No']]
    return curnode['Gain']  # Return leaf value


"""
___  _    ____ ___ ____ 
|__] |    |  |  |  [__  
|    |___ |__|  |  ___] 
                        
"""


def plot_importance(importance):
    for col in scores.keys():
        fig = px.bar(
            importance,
            y=col,
            hover_data=importance.columns,
            title=col + '\n(' + scores[col] + ")",
            width=900,
            height=250
        )
        fig.update_layout(xaxis_title="Feature")
        fig.show()
        print("Top-10 features according to this measure:")
        display(importance.sort_values([col], ascending=False).head(10))


# %%
