"""
System Utilities
--------------------------
This is a core module of MAICA that includes base utilities of the library.
"""


import torch


# Global configurations of machine learning algorithms.
run_gpu = False


def set_gpu_runnable(runnable: bool):
    """
    Set GPU enable for running machine learning algorithm in GPU.

    :param runnable: A flag to indicate the GPU enable.
    :return: None

    Example:

    >>> set_gpu_runnable(True) # Enable GPU.
    """

    if torch.cuda.is_available():
        global run_gpu
        run_gpu = runnable
    else:
        print('GPU is not available in your system. Make sure the CUDA Driver is installed in the system.')
