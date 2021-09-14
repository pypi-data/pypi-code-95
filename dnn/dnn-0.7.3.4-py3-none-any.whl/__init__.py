__version__ = "0.7.3.4"

from .layers import layers
import glob, os, shutil

def clear_session ():
    import tensorflow as tf
    tf.keras.backend.clear_session ()

def get_memory_usage ():
    import psutil
    return psutil.virtual_memory()._asdict() ['percent']

def get_gpu_memory():
    import subprocess as sp
    _output_to_list = lambda x: x.decode ('ascii').split('\n')[:-1]
    COMMAND = "nvidia-smi --query-gpu=memory.total --format=csv"
    memory_free_info = _output_to_list(sp.check_output(COMMAND.split()))[1:]
    memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
    return memory_free_values

def split_gpus (count = 2, memory = 5000): # MB
    import tensorflow as tf
    phisical_gpus = tf.config.experimental.list_physical_devices("GPU")
    tf.config.experimental.set_virtual_device_configuration(
        phisical_gpus[0],
        [tf.config.experimental.VirtualDeviceConfiguration(memory_limit = memory) for _ in range (count) ]
    )

def setup_gpus (memory_limit = 'growth', gpu_devices = []):
    # memory_limit unit is MB
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    if memory_limit and gpus:
        if gpu_devices:
            visibles = [gpus [i] for i in gpu_devices]
        else:
            visibles = gpus

        for gpu in visibles:
            if memory_limit == 'growth':
                tf.config.experimental.set_memory_growth (gpu, True)
            else:
                tf.config.set_logical_device_configuration (gpu, [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=memory_limit)])
        tf.config.set_visible_devices(visibles, 'GPU')

def processing (train_func, *args):
    from multiprocessing import Pool
    with Pool(1) as p:
        return p.apply (train_func, args)
subprocess = processing

def get_last_checkpoint (train_dir):
    cks = glob.glob (os.path.join (train_dir, 'checkpoint', '*.ckpt.index'))
    if not cks:
        raise IOError ('no checkpoint found')
    best = sorted (cks) [-1]
    return best [:-6]

def reset_dir (train_dir):
    os.path.isdir (train_dir) and shutil.rmtree (train_dir)

def get_assets_dir (train_dir):
    return os.path.join (train_dir, 'assets')

def inspect_train_dir (train_dir, restore = True):
    if not restore:
        reset_dir (train_dir)

    try:
        last = get_last_checkpoint (train_dir)
    except IOError:
        return 0, None
    return int (os.path.basename (last).split ('.')[0]), get_last_checkpoint (train_dir)

def split (*sets, test_size = 500, random_state = 42):
    from sklearn.model_selection import train_test_split
    import random

    return train_test_split (*sets, test_size = test_size, random_state = random_state or random.randrange (100))

def balanced (xs, ys, max_items = 0, onehot = False):
    import numpy as np

    classes = {}
    for idx, y in enumerate (ys):
        if onehot:
            y = np.argmax (y)
        if y not in classes:
            classes [y] = []
        classes [y].append (idx)

    if not max_items:
        max_items = min ([ len (v) for k, v in classes.items () ])

    selected = {}
    bxs, bys = [], []
    while 1:
        for k in list (classes.keys ()):
            if k not in selected:
                selected [k] = 0
            if selected [k] == max_items or not classes [k]:
                del classes [k]
                continue
            idx = classes [k].pop (0)
            bxs.append (xs [idx])
            bys.append (ys [idx])
            selected [k] += 1
        if not classes:
            break
    return bxs, bys
