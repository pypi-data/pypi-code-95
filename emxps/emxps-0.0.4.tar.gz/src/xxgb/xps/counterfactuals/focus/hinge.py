import numpy as np
import tensorflow as tf


def filter_hinge_loss(n_class, mask_vector, X, sigma, temperature, model_fn):
    n_input = X.shape[0]
    if not np.any(mask_vector):
        return np.zeros((n_input, n_class))

    filtered_input = tf.boolean_mask(X, mask_vector)

    if type(sigma) != float or type(sigma) != int:
        sigma = tf.boolean_mask(sigma, mask_vector)
    if type(temperature) != float or type(temperature) != int:
        temperature = tf.boolean_mask(temperature, mask_vector)

    filtered_loss = model_fn(filtered_input, sigma, temperature)

    indices = np.where(mask_vector)[0]
    zero_loss = np.zeros((n_input, n_class))
    hinge_loss = tf.tensor_scatter_nd_add(
        zero_loss,
        indices[:, None],
        filtered_loss,
    )
    return hinge_loss