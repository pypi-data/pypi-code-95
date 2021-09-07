import tensorflow as tf
from tensorflow.keras.layers import Conv2D, UpSampling2D
from tensorflow.keras.layers import Input, concatenate
from tensorflow.keras.models import Model
from tensorflow.keras.metrics import MeanIoU
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.layers import AveragePooling2D, LeakyReLU
from tensorflow.keras.layers import GlobalAveragePooling2D
from .loss_functions_semantic import focal_tversky_loss


def semantic_segmentation(pretrained_weights, optimizer, num_classes, input_size):
    """
    Returns a Semantic segmentation model

    :param pretrained_weights: pretrained weight matrix
    :type pretrained_weights: numpy ndarray
    :param input_size: image dimension tuple => (img_height, img_width, input_channel)
    :type input_size: tuple
    :param optimizer: optimization strategy
    :type optimizer: optimizer object
    :param num_classes: number of target classes
    :type num_classes: int
    :returns compiled Keras model
    :rtype: Keras model object
    """
    inputs = Input(input_size)

    lrelu = LeakyReLU(0.2)

    # Encoder
    conv1 = Conv2D(
        16, 1, dilation_rate=(1, 1), padding="same", kernel_initializer="he_normal"
    )(inputs)
    conv1 = BatchNormalization()(conv1)
    conv1 = lrelu(conv1)
    conv1 = Conv2D(
        16, 3, dilation_rate=(2, 2), padding="same", kernel_initializer="he_normal"
    )(conv1)
    conv1 = BatchNormalization()(conv1)
    conv1 = lrelu(conv1)

    conv2 = Conv2D(
        32, 1, dilation_rate=(1, 1), padding="same", kernel_initializer="he_normal"
    )(conv1)
    conv2 = BatchNormalization()(conv2)
    conv2 = lrelu(conv2)
    conv2 = Conv2D(
        32, 3, dilation_rate=(2, 2), padding="same", kernel_initializer="he_normal"
    )(conv2)
    conv2 = BatchNormalization()(conv2)
    conv2 = lrelu(conv2)

    conv3 = Conv2D(
        64, 1, dilation_rate=(1, 1), padding="same", kernel_initializer="he_normal"
    )(conv2)
    conv3 = BatchNormalization()(conv3)
    conv3 = lrelu(conv3)
    conv3 = Conv2D(
        64, 3, dilation_rate=(2, 2), padding="same", kernel_initializer="he_normal"
    )(conv3)
    conv3 = BatchNormalization()(conv3)
    conv3 = lrelu(conv3)

    conv4 = Conv2D(
        128, 1, dilation_rate=(1, 1), padding="same", kernel_initializer="he_normal"
    )(conv3)
    conv4 = BatchNormalization()(conv4)
    conv4 = lrelu(conv4)
    conv4 = Conv2D(
        128, 3, dilation_rate=(2, 2), padding="same", kernel_initializer="he_normal"
    )(conv4)
    conv4 = BatchNormalization()(conv4)
    conv4 = lrelu(conv4)

    # Decoder - Pyramid Module Pooling
    red = GlobalAveragePooling2D(name="red_pool")(conv4)
    red = tf.keras.layers.Reshape((1, 1, 128))(red)
    red = Conv2D(64, 1, name="red_1_by_1")(red)
    red = UpSampling2D(
        size=(400, 1920), interpolation="bilinear", name="red_upsampling"
    )(red)

    yellow = AveragePooling2D(pool_size=(2, 2), name="yellow_pool")(conv4)
    yellow = Conv2D(64, 1, name="yellow_1_by_1")(yellow)
    yellow = UpSampling2D(size=2, interpolation="bilinear", name="yellow_upsampling")(
        yellow
    )

    blue = AveragePooling2D(pool_size=(4, 4), name="blue_pool", padding="valid")(conv4)
    blue = Conv2D(64, 1, name="blue_1_by_1")(blue)
    blue = UpSampling2D(size=4, interpolation="bilinear", name="blue_upsampling")(blue)

    green = AveragePooling2D(pool_size=(4, 8), name="green_pool", padding="valid")(
        conv4
    )
    green = Conv2D(64, 1, name="green_1_by_1")(green)
    green = UpSampling2D(
        size=(4, 8), interpolation="bilinear", name="green_upsampling"
    )(green)

    merge9 = concatenate([conv4, red, yellow, blue, green])

    output = Conv2D(256, 3, padding="same", kernel_initializer="he_normal")(merge9)
    output = lrelu(output)
    output = Conv2D(3, 1, activation="softmax", padding="same")(output)

    model = Model(inputs, output)
    model.compile(
        optimizer=optimizer,
        loss=focal_tversky_loss,
        metrics=[MeanIoU(num_classes=num_classes)],
    )

    return model
