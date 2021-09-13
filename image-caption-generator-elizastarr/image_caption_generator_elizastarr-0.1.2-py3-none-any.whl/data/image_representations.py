import keras.backend as K
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
import numpy as np

'''
This preprocessing code was given by the instructor.
'''

def get_layer_functor(model, layer_name: str):
    inp = model.input
    output = model.get_layer(layer_name).output
    return K.function([inp], [output])


def eval_layer(x, layer_functor):
    return layer_functor(x)[0]


def eval_layer_batched(model, layer_name: str, x: np.ndarray, batch_size: int):
    layer_functor = get_layer_functor(model, layer_name)
    idx = 0
    ret_vals = None
    while idx < x.shape[0]:
        if idx + batch_size > x.shape[0]:
            batch_x = x[idx:, ...]
        else:
            batch_x = x[idx:(idx+batch_size), ...]

        # Normalize to [-1, 1]
        batch_x = np.float32(
            2. * (batch_x - np.min(batch_x)) / np.ptp(batch_x) - 1)
        assert np.max(batch_x) <= 1.0
        assert np.min(batch_x) >= -1.0
        batch_vals = eval_layer(batch_x, layer_functor)

        ret_vals = batch_vals if ret_vals is None else np.concatenate(
            (ret_vals, batch_vals), 0)
        idx += batch_size
    return ret_vals


def get_image_representations(images):

    convnet = MobileNetV2(input_shape=(128, 128, 3),
                          include_top=False, weights='imagenet')
    image_representations = eval_layer_batched(convnet, 'Conv_1', images, 200)
    image_representations = image_representations.reshape(len(images), 20480)
    return image_representations
