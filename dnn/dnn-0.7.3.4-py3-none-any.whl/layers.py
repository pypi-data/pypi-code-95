import tensorflow as tf
from tensorflow.keras.utils import get_custom_objects
from .custlayers.fixed_batchnorm import FixedBatchNormalization
from .custlayers.roipool import RoiPoolingConv

def softplusk(x):
    return K.softplus(x) + 1e-10

get_custom_objects().update ({'softplusk': tf.keras.layers.Activation (softplusk)})

# layering -------------------------------------------------------------------
class Layers:
    def randrange (self, minval, maxval):
        return tf.random.uniform ([], minval=minval, maxval=maxval, dtype=tf.float32)

    def input (self, shape, name, dtype = None):
        return tf.keras.layers.Input (shape, name = name, dtype = dtype)

    def output (self, n_input, n_output, name, activation = None):
        return tf.keras.layers.Dense (units = n_output, activation = activation, name = name) (n_input)

    def concat (self, inputs, axis = 1):
        return tf.keras.layers.concatenate (inputs, axis = axis)

    def dropout (self, input, dropout_rate):
        return tf.keras.layers.Dropout (dropout_rate) (input)

    def full_connect (self, tensor):
        n_output = 1
        for d in tensor.get_shape ()[1:]:
            n_output *= int (d)
        return tf.reshape (tensor, [-1, n_output])

    def sequencial_connect (self, tensor, seq_len, n_output):
        # outputs is rnn outputs
        fc = self.full_connect (tensor)
        outputs = self.dense (fc, n_output)
        return tf.reshape (outputs, [self.n_sample, seq_len, n_output])

    def fixed_batch_norm (self, n_input, mask = None, epsilon = 1e-3, axis = -1, activation = None):
        batch_normalizer = FixedBatchNormalization (epsilon, axis = axis)
        layer = batch_normalizer (n_input, mask)
        if activation is not None:
            return tf.keras.activations.get (activation)(layer)
        return layer

    def roi_pool (self, n_input, pool_size, num_rois, mask = None):
        return RoiPoolingConv (pool_size, num_rois) (n_input, mask)

    def upsample_like (self, source, target, method = 'nearest'):
        return tf.image.resize (source, (target.shape[1], target.shape[2]), method = method)


    def batch_norm (self, n_input, activation = None, momentum = 0.99, center = True, scale = True):
        batch_normalizer = tf.keras.layers.BatchNormalization (momentum = momentum, center = center, scale = scale)
        layer = batch_normalizer (n_input)
        if activation is not None:
            return tf.keras.activations.get (activation)(layer)
        return layer

    def batch_norm_with_dropout (self, n_input, dropout_rate, activation = None, momentum = 0.99, center = True, scale = True):
        layer = self.batch_norm (n_input, activation, momentum, center = center, scale = scale)
        if dropout_rate:
            return self.dropout (layer, dropout_rate)
        return layer

    def reshape (self, input, target_shape):
        return tf.keras.layers.Reshape (target_shape) (input)

    def activation (self, input, activation, **kwargs):
        return tf.keras.layers.Activation (activation, **kwargs) (input)

    def lambda_ (self, input, function, output_shape, **kwargs):
        return tf.keras.layers.Activation (function, output_shape, **kwargs) (input)

    def mask (self, input, mask_value):
        return tf.keras.layers.Masking (mask_value) (input)

    def dense (self, n_input, n_output, activation = None, kreg = None, kinit = 'glorot_uniform', name = None, **kargs):
        return tf.keras.layers.Dense (units = n_output, activation = activation, kernel_regularizer = kreg, kernel_initializer = kinit, name = name, **kargs) (n_input)

    def flatten (self, layer):
        return tf.keras.layers.Flatten ()(layer)

    def zero_pad1d (self, input, padding = 1):
        return tf.keras.layers.ZeroPadding1D (padding = padding) (input)

    def zero_pad2d (self, input, padding = (1, 1)):
        return tf.keras.layers.ZeroPadding2D (padding = padding) (input)

    def zero_pad3d (self, input, padding = (1, 1, 1)):
        return tf.keras.layers.ZeroPadding3D (padding = padding) (input)

    def conv1d (self, n_input, filters, kernel = 2, strides = 1, activation = None,  padding = "same", kreg = None, **kwarg):
        return tf.keras.layers.Conv1D (filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation, kernel_regularizer = kreg, **kwarg) (n_input)

    def separable_conv1d (self, n_input, filters, kernel = 2, strides = 1, activation = None,  padding = "same", kreg = None):
        return tf.keras.layers.SeparableConv1D (filters, kernel, strides, activation = activation,  padding = padding, kernel_regularizer = kreg) (n_input)

    def max_pool1d (self, n_input, pool = 2, strides = 2, padding = "same"):
        return tf.keras.layers.MaxPool1D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def avg_pool1d (self, n_input, pool = 2, strides = 2, padding = "same"):
        return tf.keras.layers.AvgPool1D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def upsample1d (self, input, size = 2):
        return tf.keras.layers.UpSampling1D (size = size) (input)

    def conv2d (self, n_input, filters, kernel = (2, 2), strides = (1,1), activation = None, padding = "same", kreg = None, **kwarg):
        return tf.keras.layers.Conv2D (filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation, kernel_regularizer = kreg, **kwarg) (n_input)

    def deconv2d (self, n_input, filters, kernel = (2, 2), strides = (1,1), activation = None, padding = "same", kreg = None):
        return tf.keras.layers.Conv2DTranspose (filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation, kernel_regularizer = kreg) (n_input)

    def separable_conv2d (self, n_input, filters, kernel = (2, 2), strides = (1,1), activation = None, padding = "same", kreg = None):
        return tf.keras.layers.SeparableConv2D (filters, kernel, strides, activation = activation,  padding = padding, kernel_regularizer = kreg) (n_input)

    def max_pool2d (self, n_input, pool = (2, 2), strides = (2, 2), padding = "same"):
        return tf.keras.layers.MaxPool2D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def avg_pool2d (self, n_input, pool = (2, 2), strides = (2, 2), padding = "same"):
        return tf.keras.layers.AvgPool2D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def upsample2d (self, input, size = (2, 2)):
        return tf.keras.layers.UpSampling2D (size = size) (input)

    def conv3d (self, n_input, filters, kernel = (2, 2, 2), strides = (1, 1, 1), activation = None, padding = "same", kreg = None, **kwarg):
        return tf.keras.layers.Conv3D (filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation, kernel_regularizer = kreg, **kwarg) (n_input)

    def deconv3d (self, n_input, filters, kernel = (2, 2, 2), strides = (1, 1, 1), activation = None, padding = "same", kreg = None):
        return tf.keras.layers.Conv3DTranspose (filters = filters, kernel_size = kernel, strides = strides, padding = padding, activation = activation, kernel_regularizer = kreg) (n_input)

    def max_pool3d (self, n_input, pool = (2, 2, 2), strides = (2, 2, 2), padding = "same"):
        return tf.keras.layers.MaxPool3D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def avg_pool3d (self, n_input, pool = (2, 2, 2), strides = (2, 2, 2), padding = "same"):
        return tf.keras.layers.AvgPool3D (pool_size = pool, strides = strides, padding = padding) (n_input)

    def upsample3d (self, input, size = (2, 2, 2)):
        return tf.keras.layers.UpSampling3D (size = size) (input)

    def global_avg_pool1d(self, input):
        return tf.keras.layers.GlobalAveragePooling1D ()(input)

    def global_avg_pool2d(self, input):
        return tf.keras.layers.GlobalAveragePooling2D ()(input)

    def global_avg_pool3d(self, input):
        return tf.keras.layers.GlobalAveragePooling3D ()(input)

    def global_max_pool1d(self, input):
        return tf.keras.layers.GlobalMaxPooling1D ()(input)

    def global_max_pool2d(self, input):
        return tf.keras.layers.GlobalMaxPooling2D ()(input)

    def global_max_pool3d(self, input):
        return tf.keras.layers.GlobalMaxPooling3D ()(input)

    def bernoulli_decode (self, input, n_output):
        y = self.dense (input, n_output, activation = tf.sigmoid)
        return tf.clip_by_value (y, 1e-8, 1 - 1e-8)

    def gaussian_encode (self, input, n_output):
        # https://github.com/hwalsuklee/tensorflow-mnist-VAE/blob/master/vae.py
        gaussian_params = self.dense (input, n_output * 2)
        mean = gaussian_params [:, :n_output]
        stddev = 1e-6 + tf.nn.softplus (gaussian_params [:, n_output:])
        y = mean + stddev * tf.random.normal (tf.shape (input=mean), 0, 1, dtype=tf.float32)
        return y, mean, stddev

    def embedding (self, inputs, size_voca, size_embed, mask_zero = True, dropout = False):
        embed = tf.keras.layers.Embedding (input_dim = size_voca, output_dim = size_embed, mask_zero = mask_zero) (inputs)
        if dropout:
            embed = self.dropout (embed)
        return embed

    def lstm (self, *args, **kargs):
        return self._rnn_impl ('LSTM', *args, **kargs)

    def gru (self, *args, **kargs):
        return self._rnn_impl ('GRU', *args, **kargs)

    def rnn (self, *args, **kargs):
        return self._rnn_impl ('SimpleRNN', *args, **kargs)

    def _rnn_impl  (self, cell, n_input, units, activation = 'tanh', return_sequences = True, return_state = False, time_major = False, dropout = 0.0, kreg = None, stateful = False, unroll = False):
        # whole_seq_output, final_memory_state, final_carry_state = lstm(inputs)
        return getattr (tf.keras.layers, cell) (
            units = units, activation = activation,
            return_sequences = return_sequences, return_state = return_state,
            time_major = time_major, dropout = dropout, kernel_regularizer = kreg,
            stateful = stateful, unroll = unroll
        ) (n_input)


    # helpers ------------------------------------------------------------------
    def dot (self, axes, *layers):
        return tf.keras.layers.Dot (axes)(list (layers))

    def add (self, *layers):
        return tf.keras.layers.Add ()(list (layers))

    def subtract (self, *layers):
        return tf.keras.layers.Subtract ()(list (layers))

    def multiply (self, *layers):
        return tf.keras.layers.Multiply ()(list (layers))

    def leakyrelu (self, x, alpha = 0.3, **kargs):
        return tf.keras.layers.LeakyReLU (alpha = alpha, **kargs) (x)

    def elu (self, x, alpha = 1.0, **kargs):
        return tf.keras.layers.ELU (alpha = alpha, **kargs) (x)

    def relu (self, x, **kargs):
        return tf.keras.layers.ReLU (**kargs) (x)

    def softmax (self, axis = -1):
        return tf.keras.layers.Softmax (axis = axis, **kwargs)

    def relu (self, x, **kargs):
        return tf.keras.layers.ReLU (**kargs) (x)

    def l1 (self, scale):
        return tf.keras.regularizers.l1 (scale)

    def l2 (self, scale):
        # return tf.contrib.layers.l2_regularizer (scale)
        return tf.keras.regularizers.l2 (scale)

    def l12 (self, scale_l1, scale_l2):
        return tf.keras.regularizers.l1_l2 (scale_l1, scale_l2)

    def max_norm (self, threshold, axes = 1):
        def max_norm_ (weights):
            clipped = tf.clip_by_norm (weights, clip_norm = threshold, axes = axes)
            clip_weights = tf.compat.v1.assign (weights, clipped, name = "max_norm")
            tf.compat.v1.add_to_collection ("max_norm", clip_weights)
            return None
        return max_norm_

layers = Layers ()
