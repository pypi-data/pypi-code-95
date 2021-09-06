import logging
from typing import Union, Iterable
import numpy as np

__all__ = [
    'np_sample',
    'random_stability',
]


def np_sample(
    a: Union[np.ndarray, int],
    n: int,
    replace: bool = False,
    seed: Union[None, int] = None,
    safe: bool = False,
) -> np.ndarray:
    """Randomly sample on axis 0 of a NumPy array

    Args:
        a (Union[np.ndarray, int]): The array to be samples, or the integer (max) for an `range`
        n (int): Number of samples to be draw
        replace (bool, optional): Repeat samples or not. Defaults to False.
        seed (Union[None, int], optional): Random seed for NumPy. Defaults to None.
        safe (bool, optional) : Safely handle `n` or not. If True and replace = False, and n > len(a), then n = len(a)

    Returns:
        np.ndarray: A random sample
    """
    if seed is not None:
        random_state = np.random.RandomState(seed)
    else:
        random_state = np.random

    # Range case
    if isinstance(a, int):
        if safe and n > a:
            n = a
        return random_state.choice(a, n, replace=replace)
    # Array sampling case
    else:
        if safe and n > len(a):
            n = len(a)
        return a[random_state.choice(a.shape[0], n, replace=replace)]


def random_stability(seed_value=0, deterministic=True, verbose=True):
    '''Set random seed/global random states to the specified value for a series of libraries:

            - Python environment
            - Python random package
            - NumPy/Scipy
            - Tensorflow
            - Keras
            - Torch

        seed_value (int): random seed
        deterministic (bool) : negatively effect performance making (parallel) operations deterministic. Default to True.
        verbose (bool): Output verbose log. Default to True.
    '''
    #pylint: disable=bare-except

    outputs = []
    try:
        import os
        os.environ['PYTHONHASHSEED'] = str(seed_value)
        outputs.append('PYTHONHASHSEED (env)')
    except:
        pass
    try:
        import random
        random.seed(seed_value)
        outputs.append('random')
    except:
        pass
    try:
        import numpy as np
        np.random.seed(seed_value)
        outputs.append('NumPy')
    except:
        pass

    # TensorFlow 2
    try:
        import tensorflow as tf
        tf.random.set_seed(seed_value)
        if deterministic:
            outputs.append('TensorFlow 2 (deterministic)')
            tf.config.threading.set_inter_op_parallelism_threads(1)
            tf.config.threading.intra_op_parallelism_threads(1)
        else:
            outputs.append('TensorFlow 2 (parallel, non-deterministic)')
    except:
        pass

    # TensorFlow 1 & Keras ? Not sure it works
    try:
        import tensorflow as tf
        from keras import backend as K
        tf.set_random_seed(seed_value)
        if deterministic:
            outputs.append('TensorFlow 1 (deterministic)')
            session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
        else:
            outputs.append('TensorFlow 1 (parallel, non-deterministic)')
            session_conf = tf.ConfigProto()
        session_conf.gpu_options.allow_growth = True
        sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
        K.set_session(sess)
        outputs.append('Keras')
    except:
        pass

    try:
        import torch
        torch.manual_seed(seed_value)
        torch.cuda.manual_seed_all(seed_value)
        if deterministic:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            outputs.append('PyTorch (deterministic)')
        else:
            outputs.append('PyTorch (parallel, non-deterministic)')

    except:
        pass
    #pylint: enable=bare-except
    if verbose:
        logging.info('Random seed (%d) set for: %s', seed_value, ", ".join(outputs))
