import tensorflow as tf
import numpy as np
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier

# def _exact_activation_by_index(X, feat_index, threshold):
#     boolean_act = tf.math.greater(X[:, feat_index], threshold)
#     return tf.logical_not(boolean_act), boolean_act

# def _approx_activation_by_index(X, feat_index, threshold, sigma):
#     activation = tf.math.sigmoid((X[:, feat_index] - threshold) * sigma)
#     return 1. - activation, activation

# def _double_activation_by_index(X, feat_index, threshold, sigma):
#     e_l, e_r = _exact_activation_by_index(X, feat_index, threshold)
#     a_l, a_r = _approx_activation_by_index(X, feat_index, threshold, sigma)
#     return (e_l, a_l), (e_r, a_r)

# def _split_node_by_index(node, X, feat_index, threshold, sigma):
#     # exact node and approximate node
#     e_o, a_o = node
#     ((e_l, a_l), (e_r, a_r)) = _double_activation_by_index(X, feat_index, threshold, sigma)
#     return ((tf.logical_and(e_l, e_o), a_l * a_o), (tf.logical_and(e_r, e_o), a_r * a_o))


def _split_approx(node, X, feat_index, threshold, sigma):
    # Root
    if node is None:
        node = 1.
    # Normal node
    activation = tf.math.sigmoid((X[:, feat_index] - threshold) * sigma)
    l_n, r_n = 1. - activation, activation
    return node * l_n, node * r_n


# def _split_exact(node, X, feat_index, threshold):
#     if node is None:
#         node = True
#     l_n, r_n = _exact_activation_by_index(X, feat_index, threshold, sigma)
#     return tf.logical_and(node, l_n), tf.logical_and(node, r_n)


def _parse_class_tree(tree, X, split_function):
    # Code is adapted from https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html
    n_classes = len(tree.classes_)
    n_nodes = tree.tree_.node_count
    children_left = tree.tree_.children_left
    children_right = tree.tree_.children_right
    feature = tree.tree_.feature
    threshold = tree.tree_.threshold
    values = tree.tree_.value

    nodes_vals = [None] * (n_nodes)
    leaf_nodes = [[] for _ in range(n_classes)]
    for i in range(n_nodes):
        curnode_val = nodes_vals[i]
        # NOT Leaf
        if (children_left[i] != children_right[i]):
            l_n, r_n = split_function(curnode_val, X, feature[i], threshold[i])
            nodes_vals[children_left[i]] = l_n
            nodes_vals[children_right[i]] = r_n
        # Leaf
        else:
            max_class = np.argmax(values[i])
            leaf_nodes[max_class].append(curnode_val)

    return leaf_nodes


def get_prob_classification_tree(tree, X, sigma):
    def split_function(node, X, feat_index, threshold):
        return _split_approx(node, X, feat_index, threshold, sigma)

    leaf_nodes = _parse_class_tree(tree, X, split_function)
    if tree.tree_.node_count > 1:
        n_classes = len(tree.classes_)
        out_l = [sum(leaf_nodes[c_i]) for c_i in range(n_classes)]
        stacked = tf.stack(out_l, axis=-1)

    else:  # sometimes tree only has one node
        only_class = tree.predict(
            tf.reshape(X[0, :], shape=(1, -1))
        )  # can differ depending on particular samples used to train each tree

        correct_class = tf.constant(
            1, shape=(len(X)), dtype=tf.float64
        )  # prob(belong to correct class) = 100 since there's only one node
        incorrect_class = tf.constant(0, shape=(len(X)), dtype=tf.float64)  # prob(wrong class) = 0
        if only_class == 1.0:
            class_0 = incorrect_class
            class_1 = correct_class
        elif only_class == 0.0:
            class_0 = correct_class
            class_1 = incorrect_class
        else:
            raise ValueError
        class_labels = [class_0, class_1]
        stacked = tf.stack(class_labels, axis=1)
    return stacked


def get_prob_classification_forest(model, X, sigma=10., temperature=1.):
    tree_l = [get_prob_classification_tree(estimator, X, sigma) for estimator in model.estimators_]

    if isinstance(model, AdaBoostClassifier):
        weights = model.estimator_weights_
    elif isinstance(model, RandomForestClassifier):
        weights = np.full(len(model.estimators_), 1 / len(model.estimators_))

    logits = sum(w * tree for w, tree in zip(weights, tree_l))

    if type(temperature) in [float, int]:
        expits = tf.exp(temperature * logits)
    else:
        expits = tf.exp(temperature[:, None] * logits)

    softmax = expits / tf.reduce_sum(expits, axis=1)[:, None]

    return softmax


def _parse_binary_tree(tree, X, split_function):
    # Code is adapted from https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html
    n_nodes = tree.tree_.node_count
    children_left = tree.tree_.children_left
    children_right = tree.tree_.children_right
    feature = tree.tree_.feature
    threshold = tree.tree_.threshold
    values = tree.tree_.value

    nodes_vals = [None] * (n_nodes)
    leaf_nodes = []
    for i in range(n_nodes):
        curnode_val = nodes_vals[i]
        # NOT Leaf
        if (children_left[i] != children_right[i]):
            l_n, r_n = split_function(curnode_val, X, feature[i], threshold[i])
            nodes_vals[children_left[i]] = l_n
            nodes_vals[children_right[i]] = r_n
        # Leaf
        else:
            # Current values of the sigmoid (1 if the node is active) * weight
            leaf_nodes.append(curnode_val * values[i])

    return leaf_nodes


def get_prob_binary_tree(tree, X, sigma):
    def split_function(node, X, feat_index, threshold):
        return _split_approx(node, X, feat_index, threshold, sigma)

    # Get results of the leafs
    leaf_nodes = _parse_binary_tree(tree, X, split_function)  # Leafs x samples

    # Sum all the leafs
    out_l = sum(leaf_nodes)

    return out_l


def get_prob_xgboost_binary(model, X, sigma=10.):
    tree_l = []
    for estimator in model.estimators_:
        est = get_prob_binary_tree(estimator, X, sigma)
        tree_l.append(est)

    # Sum tensors
    # NOTE: Binary classification
    logits = tf.add_n(tree_l)

    # Sigmoid
    sig = tf.math.sigmoid(logits)

    # Softmax
    softmax = tf.stack([1 - sig, sig], axis=1)

    return softmax


# def get_exact_classification_tree(tree, X):
#     leaf_nodes = _parse_class_tree(tree, X, _split_exact)
#     out_l = []
#     for class_name in tree.classes_:
#         out_l.append(tf.reduce_any(leaf_nodes[class_name]))
#     return tf.cast(tf.stack(out_l, axis=-1), dtype=tf.float64)

# def get_exact_classification_forest(model, feat_columns, X):
#   tree_parser = lambda x: get_exact_classification_tree(
#                               x, feat_columns, X)
#   tree_l = [tree_parser(estimator) for estimator in model.estimators_]

#   weights = model.estimator_weights_
#   logits = sum(w*tree for w, tree in zip(weights, tree_l))

#   expits = tf.exp(temperature*logits)
#   softmax = expits/tf.reduce_sum(expits, axis=1)[:, None]

#   return softmax

# def parse_boosted_classification_forest(model, feat_columns, X, sigma=1., temperature=1.):
#     tree_parser = lambda x: parse_classification_tree(x, feat_columns, X, sigma)
#     tree_l = [tree_parser(estimator) for estimator in model.estimators_]

#     weights = model.estimator_weights_
#     inter_result = {}
#     unnormalized_prob = {}
#     prob_denom = 0.
#     for class_name in model.classes_:
#         inter_result[class_name] = sum(w * tree[0][class_name] for w, tree in zip(weights, tree_l))
#         unnormalized_prob[class_name] = tf.exp(
#             temperature * sum(w * tree[1][class_name] for w, tree in zip(weights, tree_l))
#         )
#         prob_denom += unnormalized_prob[class_name]

#     max_result = tf.reduce_max(tf.stack([inter_result[class_name] for class_name in model.classes_]), axis=0)
#     exact_result = {}
#     prob_result = {}
#     for class_name in model.classes_:
#         exact_result[class_name] = tf.greater_equal(inter_result[class_name], max_result)
#         exact_result[class_name] = tf.cast(exact_result[class_name], tf.float64)
#         prob_result[class_name] = unnormalized_prob[class_name] / prob_denom

#     return exact_result, prob_result
