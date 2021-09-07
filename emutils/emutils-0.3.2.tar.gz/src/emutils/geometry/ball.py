import logging
import numpy as np

__all__ = [
    'generate_random_points_inside_balls',
    'generate_random_point_inside_balls',
    'generate_random_points_inside_ball',
    'generate_random_point_inside_ball',
]


# %%
def generate_random_points_inside_balls(
    X,
    normalizer,
    mode,
    phi,
    n=1,
    model=None,
    different_prediction=False,
):

    if different_prediction and model is None:
        raise ValueError('You must pass the model in order to filter points.')

    if not different_prediction and model is not None:
        logging.warning('Model passed to `generate_random_points_inside_balls` but `different_prediction = False`.')

    # Ball diameter
    diameter = normalizer.feature_deviation(method=mode, phi=phi)

    nb_features = X.shape[1]

    def __shift(x, n, p=None):
        if n == 0:
            return np.array([]).reshape(0, nb_features)

        # Sample
        Epsilon = np.random.rand(n, nb_features) - .5
        X_prime = normalizer.shift(
            np.tile(x, (n, 1)),
            shifts=np.tile(diameter, (n, 1)) * Epsilon,
            method=mode,
        )
        if p is not None:
            X_prime_ = X_prime[model.predict(X_prime) == p]
            # Recursively call the function if not enough samples are generated
            return np.concatenate([X_prime_, __shift(x, n=n - len(X_prime_), p=p)], axis=0)
        else:
            return X_prime

    if different_prediction:
        preds = model.predict(X)
        return np.array([__shift(x, n, p) for x, p in zip(X, preds)])
    else:
        return np.array([__shift(x, n) for x in X])


def generate_random_point_inside_balls(X, *args, **kwargs):
    return generate_random_points_inside_balls(X, *args, n=1, **kwargs)[:, 0, :]


def generate_random_points_inside_ball(x, *args, **kwargs):
    return generate_random_points_inside_balls(np.array([x]), *args, **kwargs)[0]


def generate_random_point_inside_ball(x, *args, **kwargs):
    return generate_random_points_inside_ball(x, *args, n=1, **kwargs)[0]


# %%
