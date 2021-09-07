# Python Standard Library
import os
import sys
import pip as piplib
import json
import time
import subprocess
import threading
import signal
import shutil
from abc import ABCMeta
from functools import reduce
import operator
from typing import Union, Iterable

# Basics
import numpy as np
import pandas as pd

# NOTE: Heavy/Optional Imports are done at function-level

__all__ = [
    'shell_command',
    'import_with_auto_install',
    'NumpyJSONEncoder',
    'np_normalize',  # Deprecation candidate
    'is_monotonic',
    'pandas_max',
    'get_conda_env',
    'static_vars',
    'eprint',
    'show_scipy_config',
    'show_torch_config',
    'scipy_config',
    'torch_config',
    'mkdir_ifnotexist',
    'mkdirname_ifnotexist',
    'prod',
    'plot_pandas_categorical_features',
    'print_estimated_execution_time',
    'Singleton',
    'pandas_hist',  # Deprecation candidate
    'clean_old_wandb_runs',  # Deprecation candidate
    'show_dataset_sample',  # Deprecation candidate
]


def shell_command(
    commands: Union[str, Iterable[str]],
    print_output: bool = True,
    timeout: Union[int, None] = None,
    kill_timeout: Union[int, None] = 10,
    verbose=2,
    **kwargs,
) -> int:
    """Run a command on the shell

    Args:
        commands (Union[str, Iterable[str]]): List of commands (List[str]) or single (str) command.
        timeout (Union[int, None], optional): Timeout (seconds) after which to kill the process. Default to None.
        kill_timeout (Union[int, None], optional): Timeout (seconds) after which to terminate the process (after kill). Default to 10 (seconds).
        print_output (bool, optional): Live-print the ouput of the commands. Defaults to True.

    Returns:
        int : Return code
    """
    if isinstance(commands, str):
        commands = [commands]

    command = ";".join(commands)

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        bufsize=0,
        **kwargs,
    ) as p:
        try:
            if print_output:
                # Print input commands
                for command in commands:
                    print("$ ", command)

                # Function to print the ouput (it's blocking)
                def print_output(out):
                    for c in iter(lambda: p.stdout.read(1), b''):
                        sys.stdout.buffer.write(c)
                        sys.stdout.flush()
                    out.close()

                # Start a separate thread to print the output
                print_thread = threading.Thread(target=print_output, args=(p.stdout, ))
                print_thread.start()

            # Wait for the process to end or the timeout to expire
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            if verbose >= 2:
                print('Timeout Expired. Killing the process.')
            p.kill()
            try:
                p.wait(timeout=kill_timeout)
            except subprocess.TimeoutExpired:
                if verbose >= 1:
                    print('Killing Timeout Expired. Terminating the process.')
                p.kill()
                p.kill()
                p.kill()
                p.terminate()
                p.terminate()
                p.terminate()

        ret_code = p.wait()
        if verbose >= 1:
            print(f'Process existed with code {ret_code}')

        # Wait for the printing to finish
        if print_output:
            if verbose >= 3:
                print('Waiting for the output to end.')
            print_thread.join()

        return ret_code


def import_with_auto_install(
    package: str,
    version: Union[str, None] = None,
    conda=True,
    pip=True,
):
    """Install (if necessary) and import package

    Args:
        package (str): Package name
        version (Union[str, None], optional): Version requirements. Defaults to None.
        conda (bool, optional): Use conda. Default to True.
        pip (bool, optional): Use pip (as fallback for conda). Default to True.

    Returns:
        Package
    """
    version = version or ""
    package_with_version = package + version

    try:
        try:
            try:
                return __import__(package)
            except ImportError:
                if conda:
                    print(f'Installing {package_with_version} using CONDA')
                    shell_command(f'conda install -y {package_with_version}', verbose=0)
            return __import__(package)
        except ImportError:
            if pip:
                print(f'Installing {package_with_version} using PIP')
                piplib.main(['install', package_with_version])
        return __import__(package)
    except ImportError:
        if pip:
            print(f'Installing {package_with_version} using PIP --user')
            piplib.main(['install', '--user', package_with_version])
    return __import__(package)


class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyJSONEncoder, self).default(obj)


def np_normalize(a):
    return a / a.sum()


def is_monotonic(a, strong=False):
    """
        Check if a vector is monotonic (or strongly monotonic)
    """
    if len(a) <= 1:
        return True

    increments_ = np.array([a[i + 1] - a[i] for i in range(len(a) - 1)])
    if strong:
        return np.all(increments_ > 0) or np.all(increments_ < 0)
    else:
        return np.all(increments_ >= 0) or np.all(increments_ <= 0)


def pandas_max(rows: Union[int, None] = None, columns: Union[int, None] = None):
    """Set the Detaframe's maximum number of rows and columns to show in Jupyter Notenooks

    Args:
        rows (Union[int, None], optional): Number of rows. Defaults to None.
        columns (Union[int, None], optional): Number of columns. Defaults to None.
    """
    if rows:
        pd.options.display.max_rows = rows
    if columns:
        pd.options.display.max_columns = columns


def get_conda_env() -> Union[str, None]:
    """Return current conda environment name

    Returns:
        Union[str, None]: Current conda environment name (if any), otherwise None.
    """
    if "envs" in sys.executable:
        return os.path.basename(os.path.dirname(os.path.dirname()))
    else:
        return None


def static_vars(**kwargs):
    """Decorator to create static variables for a function

    Usage:
    ```python
    @static_vars(i = 0)
    def function(x):
        i += 1
        return x + i

    function(0) # 1
    function(0) # 2
    function(10) # 13
    ```
    """
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def eprint(*args, **kwargs):
    """
    Prints on stderr
    """
    return print(*args, file=sys.stderr, **kwargs)


def show_dataset_sample(dataset, sample_size=10):
    import random

    for text in random.sample(dataset, sample_size):
        print(text)
        print('---------------------------------')


def show_scipy_config():
    import scipy
    return scipy.show_config()


def show_torch_config():
    import torch
    import sys
    print('__Python VERSION:', sys.version)
    print('__pyTorch VERSION:', torch.__version__)
    print('__CUDA VERSION')
    from subprocess import call
    print('__CUDNN VERSION:', torch.backends.cudnn.version())
    print('__Number CUDA Devices:', torch.cuda.device_count())
    print('__Devices')
    call(["nvidia-smi", "--format=csv", "--query-gpu=index,name,driver_version,memory.total,memory.used,memory.free"])
    print('Active CUDA Device: GPU', torch.cuda.current_device())

    print('Available devices ', torch.cuda.device_count())
    print('Current cuda device ', torch.cuda.current_device())

    for d in range(torch.cuda.device_count()):
        prop = torch.cuda.get_device_properties(d)
        print(
            prop.name, '{:,.0f}MB'.format(prop.total_memory / (1024)**2), prop.multi_processor_count, 'CUDA processors',
            'v{0}.{1}'.format(prop.major, prop.minor)
        )


scipy_config = show_scipy_config
torch_config = show_torch_config


def clean_old_wandb_runs(dir_name, dir_file, wandb_dir='wandb'):
    for run_dir in os.listdir(wandb_dir):
        if os.path.isdir(os.path.join(wandb_dir, run_dir)):
            if dir_name not in list(os.listdir(os.path.join(wandb_dir, run_dir))):
                shutil.rmtree(os.path.join(wandb_dir, run_dir))
            else:
                if dir_file not in list(os.listdir(os.path.join(wandb_dir, run_dir, dir_name))):
                    shutil.rmtree(os.path.join(wandb_dir, run_dir))


def mkdir_ifnotexist(path):
    if not os.path.exists(path):
        return os.makedirs(path)


def mkdirname_ifnotexist(path):
    # Let's get the containing directory name
    dirname = os.path.dirname(path)

    # If the file is in the current directory we skip
    if dirname == '':
        return
    return mkdir_ifnotexist()


def prod(iterable):
    """
        Chain the * operator on a list of elements
        -> i.e. equivalent of 'sum' for + operator
    """
    return reduce(operator.mul, iterable, 1)


def __subplots(df, func, cols=2, width=8, height=5, logscale=False, **kwargs):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(width * cols, height * int(np.ceil(len(df.columns) / cols))))
    for c, col in enumerate(df):
        plt.subplot(int(np.ceil(len(df.columns) / cols)), cols, c + 1)
        func(col, **kwargs)
        if logscale:
            plt.yscale('log')
        plt.title(col)
        plt.grid(alpha=.1)
    plt.show()


def plot_pandas_categorical_features(df, **kwargs):

    import seaborn as sns

    def func(col, **kwargs):
        counts = df[col].value_counts().sort_values().to_dict()
        sns.barplot(y=list(counts.keys()), x=list(counts.values()), orient='h')

    __subplots(df, func, **kwargs)


def pandas_hist(df, **kwargs):
    import matplotlib.pyplot as plt

    def func(col, **kwargs):
        df[col].hist(**kwargs)

    __subplots(df, func, **kwargs)


# def list_diff(A, B, inplace = False):
#     B = deepcopy(B)


def print_estimated_execution_time(nb_op, duration, nb_processes=1, unit='auto'):
    def get_sec(tot):
        return tot, 'second'

    def get_mins(tot):
        return tot / 60, 'minute'

    def get_hours(tot):
        return tot / 3600, 'hour'

    def get_days(tot):
        return tot / 3600 / 24, 'day'

    def get_value_and_unit(tot, unit):
        if 'sec' in unit or (unit == 'auto' and tot < 120):
            value, unit = get_sec(tot)
        elif 'min' in unit or (unit == 'auto' and tot < 7200):
            value, unit = get_mins(tot)
        elif 'hour' in unit or (unit == 'auto' and tot < 3600 * 30):
            value, unit = get_hours(tot)
        else:
            value, unit = get_days(tot)
        return value, unit

    tot = nb_op * duration / nb_processes
    duration, duration_unit = get_value_and_unit(duration, unit)
    value, unit = get_value_and_unit(tot, unit)

    print('- Number of operations: {:d}'.format(nb_op))
    print(
        '- Average execution time per operation: {:.1f} {:s}{:s}'.format(
            duration, duration_unit, "s" if duration > 1 else ""
        )
    )
    print('- Number of parallel processes: {:d}'.format(nb_processes))
    print('>>> Estimated total execution time is {:.1f} {:s}{:s}'.format(value, unit, "s" if value > 1 else ""))


class Singleton(ABCMeta):
    """
    Singleton META-CLASS from https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    Usage Example:
    class Logger(metaclass=Singleton):
        pass

    What it does:
    When you call logger with Logger(), Python first asks the metaclass of Logger, Singleton, what to do, 
    allowing instance creation to be pre-empted. This process is the same as Python asking a class what to do 
    by calling __getattr__ when you reference one of it's attributes by doing myclass.attribute.

    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]