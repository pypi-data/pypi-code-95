import time
import importlib
import inspect
import os
import sys
from pathlib import Path
import boss.keywords as bkw

import numpy as np


def twoDfloatarray_line(arr, shape1, shape2, formatString=" %8.3E"):
    if arr is None:
        return " none"
    arr = np.array(arr)
    s = ""
    for i in range(shape1):
        for j in range(shape2):
            s += formatString % (arr[i, j])
        s += ";   "
    return s[:-4]


def oneDarray_line(arr, length, type_, float_format=" %8.3E"):
    if arr is None:
        return " none"
    if type_ is str or type_ is bool:
        formatString = " %s"
    elif type_ is int:
        formatString = " %i"
    elif type_ is float:
        formatString = float_format
    s = ""
    for i in range(length):
        s += formatString % (arr[i])
    return s


def data_line(X, Q=None, fstr="%15.7E", separ="     "):
    """
    Returns a line of data. X and Q (optional) should be
    1D arrays/lists.
    """
    s = ""
    X = np.atleast_1d(X)
    for i in range(len(X)):
        if X[i] is not None:
            s += fstr % (X[i])
        else:
            fmt = "%" + str(_format_space(fstr)) + "s"
            s += fmt % ("none")
    if Q is not None:
        s += separ
        Q = np.atleast_1d(Q)
        for i in range(len(Q)):
            if Q[i] is not None:
                s += fstr % (Q[i])
            else:
                fmt = "%" + str(_format_space(fstr)) + "s"
                s += fmt % ("none")
    return s + "\n"


def append_write(file_path, text):
    """
    Writes the text into the given file appending.
    """
    f = open(file_path, "a")
    f.write(text)
    f.close()


def overwrite(file_path, text):
    """
    Writes the text into the given file overwriting.
    """
    f = open(file_path, "w")
    f.write(text)
    f.close()


def write_cols(
    file_path, vectorList, space="    ", titleLine=None, formatString="%15.7E"
):
    """
    Needs as input a vector of form [ [column1 elements], [column2 elements], ...  ]
    """
    f = open(file_path, "w")

    if titleLine is not None:
        f.write(titleLine + "\n")

    num_cols = len(vectorList)
    num_elements = len(
        vectorList[0]
    )  # number of elements must be the same in all columns

    for elem in range(num_elements):
        for col in range(num_cols):
            item = vectorList[col][elem]
            if item == "none":
                fmt = formatString[:-3] + "s"
                f.write(fmt % (item) + space)
            else:
                f.write(formatString % (float(item)) + space)

        f.write("\n")

    f.close()


def read_cols(file_path, skiprows=1):
    """
    Reads data columns from a file into a numpy array, where each column is
    separated like col1 = arr[:,0], col2 = arr[:,1] etc.
    """
    return np.loadtxt(file_path, skiprows=skiprows)


def _format_space(fmt_str, error_default=15):
    fmt_str = fmt_str.replace(" ", "")
    if fmt_str[0] == "%" and len(fmt_str) > 2:
        fmt_str = fmt_str[1:-1]
        return int(fmt_str.split(".")[0])
    else:
        return error_default
