import os
from contextlib import contextmanager
from os import listdir
from os.path import join


def file_list(root_dir):
    result = []
    if not os.path.isdir(root_dir):
        return result

    for f in listdir(root_dir):
        file_stats = os.stat(join(root_dir, f))
        result.append(
            {'name': f, 'size': file_stats.st_size, 'modified': file_stats.st_mtime}
        )
    return result


ONE_LINE_PRINT = '¡í€'


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDCOLOR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def getProgressBar(
    iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'
):
    """
    Adapted with love from https://stackoverflow.com/a/34325723

    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    BAR_COLOR = bcolors.OKBLUE
    EMPTY_CHARACTER = '-'
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + EMPTY_CHARACTER * (length - filledLength)
    return f'{ONE_LINE_PRINT}{prefix} |{BAR_COLOR}{bar}{bcolors.ENDCOLOR}| {percent}% {suffix}'


@contextmanager
def open_file_w_auto_close(filename, mode='rb'):
    f = open(filename, mode=mode)
    try:
        yield f
    finally:
        f.close()
