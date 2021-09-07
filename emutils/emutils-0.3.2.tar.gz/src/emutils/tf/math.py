import tensorflow as tf


def cov(x):
    mean_x = tf.reduce_mean(x, axis=0, keepdims=True)
    mx = tf.matmul(tf.transpose(mean_x), mean_x)
    vx = tf.matmul(tf.transpose(x), x) / tf.cast(tf.shape(x)[0], tf.float64)
    cov_xx = vx - mx
    return cov_xx


def inv_cov(x):
    return tf.linalg.inv(cov(x))
