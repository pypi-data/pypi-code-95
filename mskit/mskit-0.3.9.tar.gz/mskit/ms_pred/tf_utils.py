import numpy as np
import tensorflow as tf
from tensorflow.python import pywrap_tensorflow


def count_param_num(ckpt_path, show_single_varible=False):
    with tf.Graph().as_default():
        reader = pywrap_tensorflow.NewCheckpointReader(ckpt_path)
        all_variables = reader.get_variable_to_shape_map()

        # print(all_variables)
        total_parameters = 0
        for key in all_variables:

            shape = np.shape(reader.get_tensor(key))
            shape = list(shape)
            # print(reader.get_tensor(key))
            # print('dims', len(shape))
            variable_parameters = 1
            for dim in shape:
                # print(dim)
                variable_parameters *= dim
            total_parameters += variable_parameters

            if show_single_varible:
                print('=' * 30)
                print(key)
                print('Shape:', shape)
                print('Parameters of current variable:', variable_parameters)
        print('=' * 30)
        print(f'{total_parameters} parameters ({total_parameters / 1000:.3f}K) ({total_parameters / 1000000:.3f}M)')


def count_flops(graph):
    flops = tf.profiler.profile(graph, options=tf.profiler.ProfileOptionBuilder.float_operation())
    print('FLOPs: {}'.format(flops.total_float_ops))
