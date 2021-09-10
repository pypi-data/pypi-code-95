from sklearn.base import BaseEstimator
from sklearn.utils import check_random_state
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from sklearn.metrics import confusion_matrix
from dataclasses import dataclass
from typing import Optional, List


def out_of_bag_indices(bag_indices, dataset_length):
    bag_set = set(bag_indices)
    return np.array([x for x in range(dataset_length) if x not in bag_set], dtype=np.int)


def sample_bag(random_state, X, y):
    bag_indices = random_state.randint(0, len(X), len(X))
    bag_X, bag_y = X[bag_indices], y[bag_indices]
    return bag_indices, bag_X, bag_y


def create_confusion_matrix(classifier, bag_indices, X, y):
    """
    Creates confusion matrix where:
        rows (first index): true label, cols (second index): predicted label
    """
    oob_indices = out_of_bag_indices(bag_indices, len(X))
    oob_X, oob_y = X[oob_indices], y[oob_indices]
    pred_y = classifier.predict(oob_X)
    return confusion_matrix(y[oob_indices], pred_y)


def create_row_normalized_confusion_matrix(confmat, e):
    """
    Creates smoothed row-normalized confusion matrix where:
        rows (first index): true label, cols (second index): predicted label
    This matrix contains values from Formula 7 in the paper.
    """
    row_sums = confmat.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    row_normalized_confmat = confmat / row_sums
    # Possible improvement here would be to automatically set 'e' per-class based on the number of samples in the class.
    # Intuition is that the lower the number of samples the higher is the variance of the estimate. Something like
    # Hoeffding-bound (or rule-of-thumb based on log10) could perhaps be used to set e automatically.
    row_normalized_confmat[row_normalized_confmat < e] = e
    return row_normalized_confmat


def compute_log_priors(y):
    if len(y) == 0:
        return np.array([])
    counts = np.bincount(y.astype(int))
    with np.errstate(divide='ignore'):
        return np.log(counts / len(y))


@dataclass
class TreeData:
    tree: DecisionTreeClassifier
    log_row_normalized_confmat: np.array
    bag_indices: Optional[np.array]


class BrForestClassifier(BaseEstimator):
    """
    Scikit-learn compatible implementation of the "Bayesian Random Forest" algorithm.
    For algorithm description see: https://ieeexplore.ieee.org/abstract/document/8616560
    """

    def __init__(
        self,
        e: float = 10e-3,
        store_bag_indices=False,
        n_estimators=100,
        criterion='gini',
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_features='auto',
        max_leaf_nodes=None,
        min_impurity_decrease=0.0,
        min_impurity_split=None,
        random_state=None,
        verbose=0
    ):
        """
        Parameters
        ----------
        e:
            Epsilon hyperparameter that is used in the voting rule if the probability measured in the OOB confusion
            matrix is 0. This accounts for variance in the confusion matrix estimation. If e == 0 then a single tree
            can decide output of the whole ensemble for the class. More details in the paper.
        store_bag_indices:
            Boolean flag indicating whether to store bag indices for each tree in its TreeData class. May
            consume nontrivial amount of memory if fitted on large data.

        Other parameters have the same meaning as in sklearn.ensemble.RandomForestClassifier
        """
        super().__init__()
        self.e = e
        self.store_bag_indices = store_bag_indices
        self.n_estimators = n_estimators
        self.criterion = criterion
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.max_features = max_features
        self.max_leaf_nodes = max_leaf_nodes
        self.min_impurity_decrease = min_impurity_decrease
        self.min_impurity_split = min_impurity_split
        self.random_state = random_state
        self.verbose = verbose

        self.trees: List[TreeData] = []
        self.log_class_priors = None

    def fit(self, X, y):
        y = y.astype(int)
        if max(y) >= len(set(y)):
            raise AttributeError(
                "Labels 'y' need to be indexed from 0 and continuous. You can use scikit.preprocessing.LabelEncoder.")
        self.random_state = check_random_state(self.random_state)
        self.log_class_priors = compute_log_priors(y)
        for i in range(self.n_estimators):
            self.trees.append(self.create_tree_(X, y))
        return self

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def predict_proba(self, X):
        log_probabilities = np.tile(self.log_class_priors, (X.shape[0], 1))
        for tree_data in self.trees:
            # Potential room for improvement of the algorithm. Use soft probabilities from predict_proba instead of
            # predict. In very deep trees it is not as relevant as predict_proba tends to be very close to dirac delta.
            y_pred = tree_data.tree.predict(X)
            log_probabilities += tree_data.log_row_normalized_confmat[:, y_pred].transpose()
        probabilities = np.exp(log_probabilities)
        return probabilities / np.sum(probabilities, axis=1, keepdims=True)

    def create_tree_(self, X, y):
        bag_indices, bag_X, bag_y = sample_bag(self.random_state, X, y)
        classifier = DecisionTreeClassifier(
            criterion=self.criterion,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            min_weight_fraction_leaf=self.min_weight_fraction_leaf,
            max_features=self.max_features,
            max_leaf_nodes=self.max_leaf_nodes,
            min_impurity_decrease=self.min_impurity_decrease,
            min_impurity_split=self.min_impurity_split,
            random_state=self.random_state
        )
        classifier.fit(bag_X, bag_y)
        confmat = create_confusion_matrix(classifier, bag_indices, X, y)
        return TreeData(
            tree=classifier,
            log_row_normalized_confmat=np.log(create_row_normalized_confusion_matrix(confmat, self.e)),
            bag_indices=bag_indices if self.store_bag_indices else None
        )