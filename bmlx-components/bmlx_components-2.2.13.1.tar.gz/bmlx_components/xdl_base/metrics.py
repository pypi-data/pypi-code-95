import tensorflow as tf


def pctr(loss, y_pred, labels, weights):
    pctr = []
    for i in range(labels.shape[1]):
        _, tmp_metrics_val = tf.metrics.mean(y_pred[:, i], weights[:, i])
        pctr.append(tf.reshape(tmp_metrics_val, [1, 1]))
    return tf.squeeze(tf.concat(pctr, 1))


def actr(loss, y_pred, labels, weights):
    actr = []
    for i in range(labels.shape[1]):
        _, tmp_metrics_val = tf.metrics.mean(labels[:, i], weights[:, i])
        actr.append(tf.reshape(tmp_metrics_val, [1, 1]))
    return tf.squeeze(tf.concat(actr, 1))
