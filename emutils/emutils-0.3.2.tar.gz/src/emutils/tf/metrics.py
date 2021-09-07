from ..utils import import_with_auto_install
from ..geometry.metrics import get_metric_name_and_params as get_metric_name_and_params_base

# Require TF 2
tensorflow = import_with_auto_install('tensorflow', version=">=2")

EPSILON = 1e-6
EPSILON_DIAG = 1e-4


def get_metric_name_and_params(*args, **kwargs):
    return get_metric_name_and_params_base(*args, lib='tf', **kwargs)


def mahalabolis(X, Y, IV):
    """Element-wise Mahalabolis distance

    Args:
        X (tensorflow.Tensor): First tensor
        Y (tensorflow.Tensor]: Second tensor
        IV (tensorflow.Tensor): Inverse of the covariance matrix

    Returns:
        tensorflow.Tensor: Distance
    """
    XY_ = X - Y
    return tensorflow.math.sqrt(tensorflow.reduce_sum(tensorflow.multiply(tensorflow.matmul(XY_, IV), XY_), axis=-1))


def cosine_distance(X, Y):
    dist = tensorflow.keras.losses.cosine_similarity(
        X,
        Y,
        axis=-1,
    ) + 1
    dist = tensorflow.cast(dist, tensorflow.float64)
    return dist


def safe_norm2(X, epsilon):
    return tensorflow.math.sqrt(tensorflow.reduce_sum(X**2, axis=-1) + epsilon)


def dist(X, Y, metric: str, stable_approx: bool = False, epsilon: float = EPSILON, **kwargs):
    """Element-wise distance function

    Args:
        X (tensorflow.Tensor): First tensor
        Y (tensorflow.Tensor): Second tensor
        metric (str): Distance function name
        stable_approx (bool): Call the numerically stable version of the metric, optional. Default to False.
        epsilon (float): Epsilon used to stabilize unstable distance functions, optional. Default to 1e-8.
        **kwargs : Other params for the metric

    Raises:
        ValueError: Invalid distance function

    Returns:
        tensorflow.Tensor: Element-wise distance between the tensors
    """

    metric, params = get_metric_name_and_params(metric, **kwargs)

    if metric == 'euclidean':
        if stable_approx:
            return safe_norm2(X - Y, epsilon=epsilon, **params)
        else:
            return tensorflow.norm(X - Y, ord=2, axis=-1, **params)
    elif metric == 'cityblock':
        return tensorflow.norm(X - Y, ord=1, axis=-1, **params)
    elif metric == 'mahalanobis':
        return mahalabolis(X, Y, **params)
    elif metric == 'cosine':
        return cosine_distance(X, Y, **params)
    else:
        raise ValueError('Invalid metric.')


def cdist(X, *args, Y=None, **kwargs):
    """Pairwise-wise distance function

    Args:
        X (tensorflow.Tensor): First tensor
        Y (tensorflow.Tensor): Second tensor

        Other parameters of dist(...)

    Returns:
        tensorflow.Tensor: Pairwise distance between the tensors
    """
    if Y is None:
        Y = X

    X = tensorflow.expand_dims(X, 1)
    Y = tensorflow.expand_dims(Y, 0)

    D = dist(X, Y, *args, **kwargs)

    return D