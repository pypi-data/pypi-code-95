#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import operator as op
from scipy.interpolate import griddata
import MoNeT_MGDrivE.summaryStatistics as sstat


def axisRange(x):
    return [min(x), max(x)]


def calcResponseSurface(
    iX, iY, dZ,
    scalers=(1, 1, 1), mthd='linear',
    xAxis='linear', yAxis='linear',
    xLogMin=1e-10, yLogMin=1e-10,
    DXY=(5000, 5000)
):
    (xN, yN, zN) = (
            np.array([float(i/scalers[0]) for i in iX]),
            np.array([float(i/scalers[1]) for i in iY]),
            np.array([float(i/scalers[2]) for i in dZ])
        )
    (xRan, yRan, zRan) = (axisRange(i) for i in (xN, yN, zN))
    # X-Axis scale ------------------------------------------------------------
    if xAxis=='linear':
        xi = np.linspace(xRan[0], xRan[1], DXY[0])
    elif xAxis=='log':
        if xRan[0] == 0:
            xRan[0] = xLogMin
        xi = np.geomspace(xRan[0], xRan[1], DXY[0])
    # Y-Axis scale ------------------------------------------------------------
    if yAxis=='linear':
        yi = np.linspace(yRan[0], yRan[1], DXY[1])
    elif yAxis=='log':
        if yRan[0] == 0:
            yRan[0] =  yLogMin
        yi = np.geomspace(yRan[0], yRan[1], DXY[1])
    # Grid --------------------------------------------------------------------
    zi = griddata((xN, yN), zN, (xi[None, :], yi[:, None]), method=mthd)
    # Return variables
    ranges = (xRan, yRan, zRan)
    grid = (xN, yN, zN)
    surf = (xi, yi, zi)
    return {'ranges': ranges, 'grid': grid, 'surface': surf}


def getPopRepsRatios(base, trace, gIx):
    """
    Given a baseline population (mean) and the traces of an experiment (reps)
        this function calculates the fraction (repRto) of a given genotype
        index (gIx).
    Args:
        base (sum): Mean pop array
        trace (srp): Repetitions pop array
        gIx (int): Genotype index
    Returns:
        np.array: Fractions array.
    """
    (basePop, tracePops) = (base['population'], trace['landscapes'])
    ratioReps = [sstat.getPopRatio(trace, basePop, gIx) for trace in tracePops]
    ratioArr = np.asarray(ratioReps)
    return ratioArr


def compRatioToThreshold(repsRatios, thld, cmprOp=op.lt):
    """
    Given a population fraction, this function performs the comparison
        against a threshold and returns the bool array.
    Args:
        repsRatios (np.array): Fraction repetitions array (x: time, y: rep)
        thiS (float): Threshold to make the introgression comparison (0 to 1)
    Returns:
        np.array: bool array with info of days in which the comparison is true.
    """
    thresholdArray = np.apply_along_axis(cmprOp, 0, repsRatios, thld)
    return thresholdArray


def calcTTI(repRto, thiS, clipValue=None):
    """
    Given a population fraction, this function calculates the time it takes
        for the system to go below a given threshold.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        thiS (float): Threshold to make the introgression comparison (0 to 1)
    Returns:
        list: Times at which each of the repetitions goes below the given
                threshold (first time it breaks it).
    """
    if clipValue is None:
        (_, days) = repRto.shape
    else:
        days = clipValue
    thiSBool = [compRatioToThreshold(repRto, i, op.lt) for i in thiS]
    ttiS = [np.argmax(thiBool == 1, axis=1) for thiBool in thiSBool]
    clipped = [[x if x > 0 else days for x in i] for i in ttiS]
    return clipped


def calcTTO(repRto, thoS):
    """
    Given a population fraction, this function calculates the time it takes
        for the system to go above a given threshold.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        thoS (float): Threshold to make the outrogression comparison (0 to 1)
    Returns:
        list: Times at which each of the repetitions goes above the given
                threshold (last time it breaks it).
    """
    (reps, days) = repRto.shape
    thoSBool = [compRatioToThreshold(repRto, i, op.gt) for i in thoS]
    ttoS = [
        np.subtract(days, np.argmin(np.flip(thoBool), axis=1)) 
        for thoBool in thoSBool
    ]
    return ttoS


def calcWOP(repRto, thwS):
    """
    Given a population fraction, this function calculates number of days in
        which the repetition is below a given threshold (window of protection).
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        thwS (float): Threshold to make the outrogression comparison (0 to 1)
    Returns:
        list: Sum of the total of days the threshold is met (not the same as
            TTO-TTI for time-varying population sizes).
    """
    thwSBool = [compRatioToThreshold(repRto, i, op.lt) for i in thwS]
    wopS = [np.sum(thwBool, axis=1) for thwBool in thwSBool]
    return wopS


def calcMinMax(repRto):
    """
    Given a population fraction, this function calculates minimum/maximum
        fractions and the days at which they happen.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        thwS (float): Threshold to make the outrogression comparison (0 to 1)
    Returns:
        tuple: Min/max times and values.
    """
    (mni, mxi) = (repRto.min(axis=1), repRto.max(axis=1))
    mnx = np.asarray([np.where(repRto[i] == mni[i])[0][0] for i in range(len(mni))])
    mxx = np.asarray([np.where(repRto[i] == mxi[i])[0][0] for i in range(len(mxi))])
    return ((mni, mnx), (mxi, mxx), (1-mni, mnx), (1-mxi, mxx))


def getRatioAtTime(repRto, ttpS):
    """
    Given a population fraction, returns the populations at a given time.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        ttpS (int): Day at which we want to probe the population
    Returns:
        np.array: Population values.
    """
    return np.asarray([repRto[:, ttp] for ttp in ttpS])


def calcPOE(repRto, finalDay=-1, thresholds=(.025, .975)):
    """
    Given a population fraction, returns the probability of 
        elimination/replacement.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
        finalDay (int): Day at which the elimination is probed
        thresholds (float, float): Low and high thresholds to count as 
            elimination
    Returns:
        (float, float): Elimination probabilities (low and high)
    """
    (reps, days) = repRto.shape
    if finalDay == -1:
        fD = -1
    else:
        fD = finalDay
    fR = [rep[fD] for rep in repRto]
    (loTh, hiTh) = (
        [j < thresholds[0] for j in fR],
        [j > thresholds[1] for j in fR]
    )
    (pLo, pHi) = (sum(loTh)/reps, sum(hiTh)/reps)
    return (pLo, pHi)


def calcCPT(repRto):
    """
    Given a population fraction, returns cumulative amount of mosquitoes divided
        by time.
    Args:
        repRto (np.array): Fraction repetitions array (x: time, y: rep)
    Returns:
        float: Cumulative potential disease-transmitting mosquitoes.
    """
    return [np.sum(i)/repRto.shape[1] for i in repRto]


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'full') / w


def smoothDerivative(tSeries, smoothing=10):
    smooth = moving_average(tSeries, smoothing)
    gradient = np.gradient(smooth)
    return gradient


def popDerivative(tSeries, smoothing=10, magnitude=.01):
    gradient = smoothDerivative(tSeries, smoothing)
    zero_crossings = np.where(np.diff(np.sign(gradient)))[0]
    mag = [True if abs(x) > magnitude else False for x in gradient]
    return sum([a & b for (a,b) in zip(mag, zero_crossings)])


def calcDER(repRto, smoothing=10, magnitude=.01):
    return [popDerivative(i, smoothing, magnitude) for i in repRto]


def initDFsForDA(
            fPaths, header, thiS, thoS, thwS, ttpS,
            peak=['min', 'minx', 'max', 'maxx'],
            POE=False, poe=['POE', 'POF'],
            CPT=False, cpt=['CPT'], der=['DER']
        ):
    fNum = len(fPaths)
    if (POE and not CPT):
        heads = [list(header)+i for i in (thiS, thoS, thwS, ttpS, peak, poe)]
    elif (CPT and not POE): 
        heads = [list(header)+i for i in (thiS, thoS, thwS, ttpS, peak, cpt)]
    elif (POE and CPT):
        heads = [
            list(header)+i for i in (
                thiS, thoS, thwS, ttpS, peak, poe, cpt, der
            )
        ]
    else:
        heads = [list(header)+i for i in (thiS, thoS, thwS, ttpS, peak)]
    DFEmpty = [pd.DataFrame(int(0), index=range(fNum), columns=h) for h in heads]
    return DFEmpty


def filterDFWithID(df, xpid, max=7):
    xpidz = list(zip(list(df.columns)[:max], xpid))
    filters = [df[i[0]] == i[1] for i in xpidz]
    filter = list(map(all, zip(*filters)))
    return df[filter]



def loadDFFromFiles(fName, IND_RAN):
    df = pd.read_csv(fName[0])
    for filename in fName:
        df = df.append(pd.read_csv(filename))
    header = list(df.columns)
    headerInd = header[:IND_RAN]
    return (df, header, headerInd)


def loadDFFromSummary(fName):
    df = pd.read_csv(fName)
    header = list(df.columns)
    indRan = sum([i[0] == 'i' for i in header])
    headerInd = header[:indRan]
    return (df, header, headerInd)


