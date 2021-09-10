import pytest
import numpy as np
from unittest.mock import MagicMock, Mock
from sklearn.datasets import load_iris
from brforest.brforest import TreeData, out_of_bag_indices, create_confusion_matrix, BrForestClassifier, \
    sample_bag, compute_log_priors, create_row_normalized_confusion_matrix


@pytest.mark.parametrize(
    "bag_indices, dataset_length, expected",
    [
        (np.array([1, 1, 2, 3, 1]), 5, np.array([0, 4])),
        (np.array([1, 1, 2, 3, 0, 4, 1]), 5, np.array([])),
        (np.array([]), 5, np.array([0, 1, 2, 3, 4])),
    ]
)
def test_out_of_bag_indices(bag_indices, dataset_length, expected):
    assert np.array_equal(out_of_bag_indices(bag_indices, dataset_length), expected)


@pytest.mark.parametrize(
    "X, y",
    [
        (np.array([[0, 1], [1, 2], [3, 4], [5, 6]]), np.array([0, 1, 0, 0])),
        (np.array([]), np.array([])),
    ]
)
def test_sample_bag(X, y):
    bag_indices, bag_X, bag_y = sample_bag(np.random.RandomState(42), X, y)
    assert len(bag_indices) == len(X)
    assert (bag_indices >= 0).all()
    assert (bag_indices < len(X)).all()
    assert len(bag_X) == len(X)
    assert len(bag_y) == len(y)
    assert np.array_equal(X[bag_indices], bag_X)
    assert np.array_equal(y[bag_indices], bag_y)
    if len(X) > 2:
        bag_indices2, _, _ = sample_bag(np.random.RandomState(43), X, y)
        assert not np.array_equal(bag_indices, bag_indices2)


def test_create_confusion_matrix():
    classifier = MagicMock()
    classifier.predict.return_value = [0, 1, 2, 0, 0, 1]
    y = np.array([0, 1, 2, 1, 1, 2])
    X = np.array([[0], [1], [2], [3], [4], [5]])
    bag_indices = np.array([])
    confmat = create_confusion_matrix(classifier, bag_indices, X, y)
    expected = np.array([  # rows: true label, cols: predicted label
        [1, 0, 0],
        [2, 1, 0],
        [0, 1, 1]])
    assert np.array_equal(confmat, expected)


@pytest.mark.parametrize(
    "confmat, e, expected",
    [
        (np.array([[2, 4], [3, 5]]), 0, np.array([[2/6, 4/6], [3/8, 5/8]])),
        (np.array([[0, 0], [3, 5]]), 0.01, np.array([[0.01, 0.01], [3/8, 5/8]])),
    ]
)
def test_create_row_normalized_confusion_matrix(confmat, e, expected):
    result = create_row_normalized_confusion_matrix(confmat, e)
    assert np.allclose(result, expected)


@pytest.mark.parametrize(
    "y, expected",
    [
        (np.array([1, 1, 1]), np.array([-np.inf, np.log(1)])),
        (np.array([1, 1, 1, 2, 2, 2, 4]), np.array([-np.inf, np.log(3/7), np.log(3/7), -np.inf, np.log(1/7)])),
        (np.array([1., 1., 1., 2., 2., 2., 4.]), np.array([-np.inf, np.log(3/7), np.log(3/7), -np.inf, np.log(1/7)])),
    ]
)
def test_compute_log_priors(y, expected):
    assert np.allclose(compute_log_priors(y), expected)


class TestBrForestClassifier:
    @pytest.fixture
    def iris_classifier(self):
        classifier = BrForestClassifier(n_estimators=50, e=0.001, store_bag_indices=True, random_state=42)
        X, y = load_iris(return_X_y=True)
        return classifier.fit(X, y)

    def test_fit(self, iris_classifier):
        assert len(iris_classifier.trees) == 50
        assert np.allclose(iris_classifier.log_class_priors, np.log(np.array([1/3]*3)))
        for data in iris_classifier.trees:
            assert data.bag_indices is not None
            assert data.log_row_normalized_confmat.shape == (3, 3)
            assert np.allclose(np.exp(data.log_row_normalized_confmat).sum(axis=1), np.ones(shape=(3, 1)), atol=0.003)

    def test_predict(self):
        dummy = BrForestClassifier(n_estimators=50)
        dummy.predict_proba = Mock(return_value=np.array([[0.2, 0.3, 0.3], [0.5, 0.3, 0.3]]))
        assert np.array_equal(dummy.predict(np.array([1])), np.array([1, 0]))

    def test_predict_proba(self, iris_classifier):
        X, y = load_iris(return_X_y=True)
        y_pred = iris_classifier.predict_proba(X)
        assert y_pred.shape[0] == y.shape[0]
        assert np.allclose(y_pred.sum(axis=1), np.ones(y.shape))
        assert (np.sum(np.argmax(y_pred, axis=1) == y) / len(y)) > 0.99
    
    def test_predict_proba_with_mock(self):
        # In this test we assess whether the result equals to a pen&paper result on a small example
        classifier = BrForestClassifier(n_estimators=2, e=0.001)
        classifier.log_class_priors = np.log(np.array([0.7, 0.3]))
        tree1 = MagicMock()
        tree1.predict.return_value = np.array([0, 1]) 
        classifier.trees.append(
            TreeData(
                log_row_normalized_confmat=np.log(np.array([[0.9, 0.1], [0.3, 0.7]])),
                tree=tree1,
                bag_indices=None)
        )
        tree2 = MagicMock()
        tree2.predict.return_value = np.array([1, 0]) 
        classifier.trees.append(
            TreeData(
                log_row_normalized_confmat=np.log(np.array([[0.8, 0.2], [0.25, 0.75]])),
                tree=tree2,
                bag_indices=None)
        )

        x0y0 = 0.7*0.9*0.2
        x0y1 = 0.3*0.3*0.75
        x1y0 = 0.7*0.1*0.8
        x1y1 = 0.3*0.7*0.25
        expected = np.array([[x0y0, x0y1], [x1y0, x1y1]])
        expected = expected / expected.sum(axis=1, keepdims=True)

        output = classifier.predict_proba(np.array([[0], [1]]))

        assert np.allclose(output, expected)
        





