#!/usr/bin/env python
"""
tfm_utils contains Python wrappers for the TFM-Pvalue program. It allows for
accurate calculation of p-values associated with scores for a given motif PWM.
Naturally, it can also be used to calculate the score corresponding to a given
p-value for a transcription factor motif PWM.

The original program can be downloaded at:
http://bioinfo.lifl.fr/tfm-pvalue/tfm-pvalue.php

Additionally, see this paper for how the p-values and thresholds are calculated:
Efficient and accurate P-value computation for Position Weight Matrices
H. Touzet and J.S. Varre
Algorithms for Molecular Biology 2007, 2:15

Copyright (C) 2017  Jared Andrews

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import tfm_utils.pytfmpval as tfm
import psutil
from math import ceil

import os, sys
import pandas as pd
import numpy as np
import ctypes


def create_matrix(matrix_file, bg=[0.25, 0.25, 0.25, 0.25], mat_type="counts", log_type="nat"):
    """
    From a JASPAR formatted motif matrix count file, create a Matrix object.

    This function also converts it to a log-odds (position weight) matrix if necessary.

    Args:
        matrix_file (str): White-space delimited string of row-concatenated motif matrix.
        bg (list of floats): Background nucleotide frequencies for [A, C, G, T].
        mat_type (str): Type of motif matrix provided. Options are: "counts", "pfm", "pwm".
            "counts" is for raw count matrices for each base at each position.
            "pfm" is for position frequency matrices (frequencies already calculated.
            "pwm" is for position weight matrices (also referred to as position-specific scoring matrices.)
        log_type (str): Base to use for log. Default is to use the natural log. "log2" is the other option.
            This will affect the scores and p-values.

    Returns:
        m (tfm_utils Matrix):
            Matrix in pwm format.
    """

    a, c, g, t = bg[0], bg[1], bg[2], bg[3]


    m = tfm.Matrix(a, c, g, t)
    if not os.path.exists(matrix_file):
        raise FileNotFoundError()

    m.readJasparMatrix(matrix_file)

    if mat_type.upper() == "COUNTS":
        if log_type.upper() == "NAT":
            m.toLogOddRatio()
        elif log_type.upper() == "LOG2":
            m.toLog2OddRatio()
        else:
            print("Improper log type argument, using natural log.")
            m.toLogOddRatio()

    return m


def toPWM(df: pd.DataFrame):
    """
    Converts DFs in PPM (position probability matrix) or PCM (position count matrix) and forces then
    to PWM (position weight matrix format.

    .. math::
        \sum_{i=1}^{\\infty} x_{i}

    Args:
        df (pd.DataFrame):  Takes a dataframe with appropriate columns or rows in any of the following forms

    Returns:

    """
    # rule 1: if all values can be casts to integers, then its almost defiantly a count matrix
    try:
        np.array(df.values).astype(int, casting="safe")
        df = orient_df(df)
        df =  df / df.sum(axis=0)
        return np.log2(df)

    except TypeError:
        pass

    # rule 2: if any of the values are negative its likely already a PWM
    if (np.array(df) < 0).any():
        return df

    # if we reach this point we assume that we are using frequency values
    else:
        # make them like log neg2 or something
        return np.log2(df)





def read_matrix(matrix, bg=[0.25, 0.25, 0.25, 0.25], mat_type="counts", log_type="nat"):
    """
    From a string of space-delimited counts create a Matrix object.

    Break the string into 4 rows corresponding to A, C, G, and T.
    This function also converts it to a log-odds (position weight) matrix if necessary.

    Args:
        matrix_file (str): White-space delimited string of row-concatenated motif matrix.
        bg (list of floats): Background nucleotide frequencies for [A, C, G, T].
        mat_type (str): Type of motif matrix provided. Options are: "counts", "pfm", "pwm".
            "counts" is for raw count matrices for each base at each position.
            "pfm" is for position frequency matrices (frequencies already calculated).
            "pwm" is for position weight matrices (also referred to as position-specific scoring matrices.)
        log_type (str): Base to use for log. Default is to use the natural log. "log2" is the other option.
            This will affect the scores and p-values.

    Returns:
        m (tfm_utils Matrix): Matrix in pwm format.
    """

    try:
        a, c, g, t = bg[0], bg[1], bg[2], bg[3]
        if (len(matrix.split()) % 4) != 0:
            raise ValueError("Uneven rows in motif matrix. Ensure rows of equal length in input.")

        m = tfm.Matrix(a, c, g, t)
        m.readMatrix(matrix)

        if mat_type.upper() == "COUNTS":
            if log_type.upper() == "NAT":
                m.toLogOddRatio()
            elif log_type.upper() == "LOG2":
                m.toLog2OddRatio()
            else:
                print("Improper log type argument, using natural log.")
                m.toLogOddRatio()

        return m

    except ValueError as error:
        print(repr(error))


def orient_df(df):
    column_names =[x.upper() for x in  df.columns if type(x) == str]
    rows = [x.upper() for x in  df.index if type(x) == str]
    if "A" in column_names and "C" in column_names and "G" in column_names and "T" in column_names:
        return df.traspose()
    elif "A" in rows and "C" in rows and "G" in rows and "T" in rows:
        return df
    else:
        raise ValueError("Columns or rows of df must include all of 'A', 'C', 'G', 'T'.")


def df_to_matrix(df, bg = [.25, .25, .25, .25]):
    """
    Converts a dataframe into the space delimited form required by the rest of the library.

    Args:
        df (pandas.DataFrame): A dataframe with the  PWM values in it. Must have columns with names "A'", "C", "T", and "G" or rows with the same name

    Returns:
        values (str): All values of the df in the correct order and space delimited

    """

    column_names =[x.upper() for x in  df.columns if type(x) == str]
    rows = [x.upper() for x in  df.index if type(x) == str]
    if "A" in column_names and "C" in column_names and "G" in column_names and "T" in column_names:
        values = np.array([df[x].values for x in ["A", "C", "G", "T"]]).flatten()

    elif "A" in rows and "C" in rows and "G" in rows and "T" in rows:
        values = np.array([df.loc[x].values for x in ["A", "C", "G", "T"]]).flatten()

    else:
        raise ValueError("DataFrame must have all of ['A', 'C' 'T' 'G'] in the column names or row index")

    string =  ' '.join([str(x) for x in values])
    return read_matrix(string, bg)


def score2pval(matrix, req_score, mem_thresh=2.0):
    """
    Determine the p-value for a given score for a specific motif PWM.

    Args:
        matrix (tfm_utils Matrix): Matrix in pwm format.
        req_score (float): Requested score for which to determine the p-value.
        mem_thresh (float): Memory in GBs to remain free to system.
            Once passed, the closest p-val approximation will be returned
            instead of the exact p-val. Should only occur rarely with very
            long and degenerate motifs. Used to help ensure the system
            won't run out of memory due to these outliers. This is only
            calculated after each pass, each of which is more time and memory
            intensive than the last, so changing this value isn't recommended
            unless accuracy out to the 8th decimal place is really necessary.

    Returns:
        pv (float): The calculated p-value corresponding to the score.
    """

    if isinstance(matrix, pd.DataFrame):
        matrix = toPWM(matrix)
        matrix = df_to_matrix(matrix)

    mem_thresh = mem_thresh * 1000 * 1024 * 1024
    granularity = 0.1
    max_granularity = 1e-10
    decrgr = 10  # Factor to increase granularity by after each iteration.

    pv = tfm.doublep()
    ppv = tfm.doublep()

    pv.assign(.001)
    ppv.assign(.001)

    while granularity > max_granularity:
        matrix.computesIntegerMatrix(granularity)

        if np.isnan(matrix.errorMax):
            matrix.errorMax = 0.01 #check if this makes any sense

        max_s = int(req_score * matrix.granularity + matrix.offset + matrix.errorMax + 1)
        min_s = int(req_score * matrix.granularity + matrix.offset - matrix.errorMax - 1)
        score = int(req_score * matrix.granularity + matrix.offset)

        matrix.lookForPvalue(score, min_s, max_s, ppv, pv)

        mem = psutil.virtual_memory()
        if mem.available <= mem_thresh:
            print("Memory usage threshold passed, returning closest approximation.")
            return pv.value()

        if ppv.value() == pv.value():
            return pv.value()

        granularity = granularity / decrgr

    print("Max granularity exceeded. Returning closest approximation.")
    return pv.value()


def pval2score(matrix, pval, mem_thresh=2.0):
    """
    Determine the score for a given p-value for a specific motif PWM.

    Args:
        matrix (tfm_utils Matrix): Matrix in pwm format.
        pval (float): p-value for which to determine the score.
        mem_thresh (float): Memory in GBs to remain free to system.
            Once passed, the closest p-val approximation will be returned
            instead of the exact p-val. Should only occur rarely with very
            long and degenerate motifs. Used to help ensure the system
            won't run out of memory due to these outliers. This is only
            calculated after each pass, each of which is more time and memory
            intensive than the last, so changing this value isn't recommended
            unless accuracy out to the 8th decimal place is really necessary.

    Returns:
        score (float): The calculated score corresponding to the p-value.
    """
    if isinstance(matrix, pd.DataFrame):
        matrix = toPWM(matrix)
        matrix = df_to_matrix(matrix)


    mem_thresh = mem_thresh * 1000 * 1024 * 1024
    init_granularity = 0.1
    max_granularity = 1e-10
    decrgr = 10  # Factor to increase granularity by after each iteration.

    pv = tfm.doublep()  # Initialize as a c++ double.
    ppv = tfm.doublep()

    pv.assign(.001)
    ppv.assign(.001)

    matrix.computesIntegerMatrix(init_granularity)

    if np.isnan(matrix.errorMax):
        matrix.errorMax = .001

    max_s = int(matrix.maxScore + ceil(matrix.errorMax + 0.5))
    min_s = int(matrix.minScore)
    granularity = init_granularity

    while granularity > max_granularity:
        matrix.computesIntegerMatrix(granularity)

        if np.isnan(matrix.errorMax):
            matrix.errorMax = .001

        score = matrix.lookForScore(min_s, max_s, pval, pv, ppv)

        min_s = int((score - ceil(matrix.errorMax + 0.5)) * decrgr)
        max_s = int((score + ceil(matrix.errorMax + 0.5)) * decrgr)

        if ppv.value() == pv.value():
            break

        mem = psutil.virtual_memory()
        if mem.available <= mem_thresh:
            print("Memory usage threshold passed, returning closest score approximation.")
            break

        granularity = granularity / decrgr

    if granularity <= max_granularity:
        print("Max granularity exceeded. Returning closest score approximation.")

    final_score = (score - matrix.offset) / matrix.granularity
    return final_score
