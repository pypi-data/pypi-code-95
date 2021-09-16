import tensorflow as tf
from keras.engine.keras_tensor import KerasTensor
from tensorflow import keras

from uberlimb.parameters import ModelArchitecture, FourierMode


def custom_activation(activation: str):
    if activation == 'sinus':
        return keras.layers.Lambda(tf.math.sin)
    elif activation == 'experimental1':
        return keras.layers.Lambda(tf.math.lgamma)
    else:
        return keras.layers.Activation(activation)


def apply_f_mode(x: KerasTensor, f_mode: FourierMode):
    if f_mode == FourierMode.DISABLED:
        pass
    elif f_mode == FourierMode.ALL:
        x = keras.layers.experimental.RandomFourierFeatures(
            2)(x)
    elif f_mode == FourierMode.XY:
        slice_1 = keras.layers.Lambda(
            lambda tensor: tf.slice(tensor, [0, 0], [-1, 2]))(x)
        slice_2 = keras.layers.Lambda(
            lambda tensor: tf.slice(tensor, [0, 2], [-1, 6]))(x)
        slice_1 = keras.layers.experimental.RandomFourierFeatures(
            2)(slice_1)
        x = keras.layers.Concatenate()([slice_1, slice_2])

    return x


def perceptron(x: KerasTensor,
               depth: int, width: int,
               initializer: keras.initializers.Initializer,
               activation: str):
    for _ in range(depth):
        x = keras.layers.Dense(width,
                               kernel_initializer=initializer)(x)
        x = custom_activation(activation)(x)
    return x


def densenet(x,
             depth,
             width,
             initializer,
             activation):
    for _ in range(depth):
        y = keras.layers.Dense(width,
                               kernel_initializer=initializer)(x)
        y = custom_activation(activation)(y)
        x = keras.layers.Concatenate()([x, y])
    return x


def resnet(x: KerasTensor,
           depth: int, width: int,
           initializer: keras.initializers.Initializer,
           activation: str):
    y = keras.layers.Dense(width,
                           kernel_initializer=initializer)(x)
    y = custom_activation(activation)(y)
    for i in range(depth - 1):
        x = keras.layers.Dense(width,
                               kernel_initializer=initializer)(x)
        x = custom_activation(activation)(x)
        x = keras.layers.Add()([x, y])
        x = custom_activation(activation)(x)
        y = x
    return x


def resnet_concat(x: KerasTensor,
                  depth: int, width: int,
                  initializer: keras.initializers.Initializer,
                  activation: str):
    y = keras.layers.Dense(width,
                           kernel_initializer=initializer)(x)
    y = custom_activation(activation)(y)
    for i in range(depth - 1):
        x = keras.layers.Dense(width,
                               kernel_initializer=initializer)(x)
        x = custom_activation(activation)(x)
        x = keras.layers.Concatenate()([x, y])
        y = x
    return x


def chain(x: KerasTensor,
          depth: int, width: int,
          initializer: keras.initializers.Initializer,
          activation: str):
    for i in range(depth):
        if i % 3 == 0:
            x = keras.layers.Dense(width,
                                   kernel_initializer=initializer)(x)
            x = custom_activation(activation)(x)
        else:
            x_1 = keras.layers.Dense(width,
                                     kernel_initializer=initializer)(x)
            x_1 = custom_activation(activation)(x_1)
            x_2 = keras.layers.Dense(width,
                                     kernel_initializer=initializer)(x)
            x_2 = custom_activation(activation)(x_2)
            x = keras.layers.Add()([x_1, x_2])
            x = custom_activation(activation)(x)
    return x


def plexus(x: KerasTensor,
           depth: int, width: int,
           initializer: keras.initializers.Initializer,
           activation: str):
    for i in range(depth):
        if i % 3 == 0:
            x = keras.layers.Dense(width,
                                   kernel_initializer=initializer)(x)
            x = custom_activation(activation)(x)
            x_1 = x
            x_2 = x
            x_3 = x
        else:
            x_1 = keras.layers.Dense(width,
                                     kernel_initializer=initializer, )(x_23)
            x_1 = custom_activation(activation)(x_1)
            x_2 = keras.layers.Dense(width,
                                     kernel_initializer=initializer)(x_13)
            x_2 = custom_activation(activation)(x_2)
            x_3 = keras.layers.Dense(width,
                                     kernel_initializer=initializer)(x_12)
            x_3 = custom_activation(activation)(x_3)
        x_12 = keras.layers.Concatenate()([x_1, x_2])
        x_13 = keras.layers.Concatenate()([x_1, x_3])
        x_23 = keras.layers.Concatenate()([x_2, x_3])
    x = keras.layers.Concatenate()([x_1, x_2, x_3])
    return x


architecture_lookup = {
    ModelArchitecture.PERCEPTRON: perceptron,
    ModelArchitecture.DENSENET: densenet,
    ModelArchitecture.RESNET: resnet,
    ModelArchitecture.RESNET_CONCAT: resnet_concat,
    ModelArchitecture.CHAIN: chain,
    ModelArchitecture.PLEXUS: plexus,
}
