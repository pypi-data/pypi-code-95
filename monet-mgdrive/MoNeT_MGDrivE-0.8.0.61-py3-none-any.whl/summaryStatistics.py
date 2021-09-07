import numpy as np
import operator as op


def reachedSteadtStateAtDay(
            aggData,
            safety=.01,
            finalFrame=-1
        ):
    """
    Description:
        * Calculates the point at which the aggregated alleles reach their
            steady state (defined by the final frame of the simulation).
            * aggData: Genotypes aggregated data.
    In:
        * safety: Envelope of values around the steady state that are
            considered "stable" (as a proportion of the final total allele
            composition).
        * finalFrame: Index of the day to be considered as "stable" for
            reference purposes.
    Out:
        * steadtStateReach: Day at which the dynamics of the system became
            stable.
    Notes:
        * This is a quick and simple way to calculate the steady state, but
            assumes that the system stabilizes and that the simulation was
            run for enough time for the dynamics to become stable.
    """
    finalFrame = aggData["population"][finalFrame]
    tolerance = round(sum(finalFrame) * safety)
    toleranceUp = finalFrame + tolerance
    toleranceDown = finalFrame - tolerance

    daysMax = len(aggData["population"])

    for i in range(0, daysMax):
        steadyStateReach = daysMax
        testFrame = aggData["population"][i]

        boolsUp = testFrame < toleranceUp
        boolsDown = testFrame > toleranceDown
        zeros = testFrame < 1

        if (all(boolsUp) and all(boolsDown)) or all(zeros):
            steadyStateReach = i
            break

    return steadyStateReach


def getTimeToMin(
            aggData,
            safety=.01
        ):
    """
    Description:
        * Calculates the point at which the total population reaches
            its minimum.
    In:
        * aggData: Genotypes aggregated data.
        * safety: Envelope of values around the steady state that are
            considered "stable" (as a proportion of the final total allele
            composition).
    Out:
        * time: Point in time at which the minimum is reached
        * popMin: Population size at its minimum
    """
    pop = [sum(row) for row in aggData['population']]
    for time in range(len(pop)):
        popMin = min(pop)
        if np.isclose(pop[time], popMin, atol=safety):
            break
    return (time, popMin)


# def comparePopToThresholds(pop, gIx, tIx, thrs, cmprOp=op.lt, refPop=0):
#     """Calculates if the genotypes at a desired index meet the condition
#         passed as fractions of the total population. This function was created
#         to calculate where the population goes below a given threshold for
#         times of suppression.
#
#     Parameters
#     ----------
#     pop : numpy array
#         Genotypes numpy array of a single population.
#     gIx : int
#         Index of the genotype of interest.
#     tIx : list of integers
#         List of the genotypes for the 'total population' calculation (for
#             fractions to be computed).
#     thrs : list of floats (0 to 1)
#         List of the thresholds to compare the population fraction against.
#     cmprOp : operator
#         Comparsion to be perfomed between pop and thrs
#             (https://docs.python.org/3/library/operator.html).
#
#     Returns
#     -------
#     numpy array of bools
#         Numpy array of bools flagging conditions being met. Each column
#             represents one of the thresholds passed in tIx for the whole
#             duration (time) of the sim (pop array's length).
#     """
#     flagsArray = np.empty((len(pop), len(thrs)), dtype=bool)
#     for (i, dayData) in enumerate(pop):
#         # Check if the pop was set to a specific value for mixed releases
#         if (refPop > 0):
#             totalPop = refPop
#         else:
#             totalPop = sum(dayData[tIx])
#         # Do the fraction comparisons
#         if (totalPop > 0):
#             fraction = (dayData[gIx] / totalPop)
#         else:
#             fraction = dayData[gIx]
#         closeFlags = [cmprOp(fraction, i) for i in thrs]
#         flagsArray[i] = closeFlags
#     return flagsArray


def countConditionDays(thrsBool):
    """Counts the number of 'true's on the thresholds bool numpy array.
            Created to calculate the number of protection days by a genotype
            or suppression.

    Parameters
    ----------
    thrsBool : numpy array of bools
        Numpy array with the met/unmet condition results
            ('comparePopToThresholds' output).

    Returns
    -------
    list
        List of days where each of the conditions is met.

    """
    return list(np.count_nonzero(thrsBool, axis=0))


def getConditionChangeDays(thrsBool):
    """Returns the days at which the conditions depitcted by the thresholds
        bools array changes state.

    Parameters
    ----------
    thrsBool : numpy array of bools
        Numpy array with the met/unmet condition results
            ('comparePopToThresholds' output).
    Returns
    -------
    list
        List of days where each of the conditions changes.

    """
    (shp, days) = (thrsBool.shape, [])
    for i in (range(shp[0] - 1)):
        (a, b) = (thrsBool[i], thrsBool[i + 1])
        change = (a ^ b)
        if (any(change)):
            days.append(i)
    return days


def calcDaysCrosses(aggregatedNodesData, thresholds, ssPops, gIx):
    """Gets the days at which the allele crosses the thresholds supplied.

    Parameters
    ----------
    aggregatedNodesData : dict
        Information for the nodes alleles data aggregated by genotypes.
    thresholds : list
        List of thresholds to get the timings.
    ssPops : list
        Steady-state populations by genotype.
    gIx : int
        Index of the genotype at the genotypes end of the dictionary.

    Returns
    -------
    list
        Times at which .

    """
    chngDays = []
    for j in range(len(aggregatedNodesData['landscape'])):
        nodePop = aggregatedNodesData['landscape'][j]
        thrsBool = comparePopToThresholds(
                nodePop, gIx, [0, 1], thresholds, refPop=ssPops[j]
            )
        chngDays.append(getConditionChangeDays(thrsBool))
    return chngDays


def getSSPopsInLandscape(aggregatedNodesData, ssDay=-1):
    """Gets the steady-state populations in a landscape assuming that they
            are in SS at the supplied day and that the last genotype contains
            the sum of all the other genotypes.

    Parameters
    ----------
    aggregatedNodesData : dict
        Information for the nodes alleles data aggregated by genotypes.
    ssDay : int
        Day at which the populations are in steady-state.

    Returns
    -------
    list
        Steady-state populations per node (total pops as defined by the
            last element of the genotypes arrays).

    """
    ssPops = []
    for node in aggregatedNodesData['landscape']:
        ssPops.append(node[ssDay - 1][-1])
    return ssPops


def getTimeToMinAtAllele(aggData, gIx, safety=.1):
    """Returns the min value of the allele in a population, along with the
        time at which this value is reached.

    Parameters
    ----------
    aggData : dict
        Information for the nodes alleles data aggregated by genotypes.
    gIx : int
        Index of the genotype at the genotypes end of the dictionary.
    safety : float
        Tolerance for the metric.

    Returns
    -------
    tuple
        Time at which the minPop is reached, and the value of the minPop.

    """
    pop = [row[gIx] for row in aggData['population']]
    for time in range(len(pop)):
        popMin = min(pop)
        if np.isclose(pop[time], popMin, atol=safety):
            break
    return (time, popMin)


###############################################################################
# Flexible time to threshold statistics
###############################################################################
def comparePopToThresh(ratioOI, thresholds, cmprOp=op.lt):
    """
    Gets a ratio population (as obtained from getPopRatio) and returns the
        array of flags where the condition is met.
    Args:
        ratioOI (np.array): Calculated by getPopRatio.
        thresholds (list): List of ratios to use as thresholds.
        cmprOp(function): Operation to compare against (less than, greater
            than, etcetera).
    Returns:
        np.array: An array of the flags where the condition is met (the
            dimensions correspond to the number of days in the simulation,
            and the number of thresholds provided in the input list).

    """
    flagsArray = np.empty((len(ratioOI), len(thresholds)), dtype=bool)
    for (i, dayData) in enumerate(ratioOI):
        closeFlags = [cmprOp(dayData, i) for i in thresholds]
        flagsArray[i] = closeFlags
    return flagsArray


def getPopRatio(prbPop, refPop, gIx):
    """
    Calculates the ratio between a probe and reference population and returns
        the result at a genotype of interest.
    Args:
        prbPop (np.array): Probe population
        refPop (np.array): Reference population
        gIx (int): Index of the genotype of interest's location
    Returns:
        list: Ratio at the genotype of interest.

    """
    (a, b) = (prbPop, refPop)
    ratio = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
    ratioOI = [row[gIx] for row in ratio]
    return ratioOI


def trueIndices(boolList):
    """
    Returns the positions where True is found.
    Args:
        boolsList (list): List of booleans to process.
    Returns:
        list: List of positions where True is present.

    """
    trueIx = [i for (i, x) in enumerate(boolList) if x == 1]
    if len(trueIx) > 0:
        return trueIx
    else:
        return [np.nan]


def thresholdMet(thsArray):
    """
    Returns the days in which the condition is met in the thresholds array
        (where True is present).
    Args:
        thsArray (np.array): Bool array of thresholds where a given condition
            is met (output form the comparePopToThresh function).
    Returns:
        list: List of days where the condition is met (True positions).
    """
    thsNum = len(thsArray[0])
    thrsMet = [None] * thsNum
    for col in range(thsNum):
        boolCol = [i[col] for i in thsArray]
        daysAbove = trueIndices(boolCol)
        thrsMet[col] = daysAbove
    return thrsMet


def calcMeanTTI(meanPrb, meanRef, thresholds, gIx, cmprOp=op.lt):
    """
    Calculates the mean time to introgression for the mean response of two
        populations.
    Args:
        meanPrb (np.array): Mean population of the probe population
        meanRef (np.array): Mean population of the reference population
        thresholds (list): List of ratios to use as thresholds.
        gIx (int): Index of the genotype of interest's location
        cmprOp(function): Operation to compare against (less than, greater
            than, etcetera).
    Returns:
        list: Returns the time at which the condition is met at a given
            quantile level.
    """
    ratioOI = getPopRatio(meanPrb['population'], meanRef['population'], gIx)
    thsArray = comparePopToThresh(ratioOI, thresholds, cmprOp=op.lt)
    thsDays = thresholdMet(thsArray)
    # Extracting the time to first cross (modify for other metrics)
    ttiAn = [i[0] for i in thsDays]
    return ttiAn


def calcQuantTTI(srpPrb, meanRef, thresholds, gIx, quantile=.95, cmprOp=op.lt):
    """
    Calculates the mean time to introgression for the quantile response of two
        populations.
    Args:
        srpPrb (dict): SRP population of the probe population.
        meanRef (np.array): Mean population of the reference population
        thresholds (list): List of ratios to use as thresholds.
        gIx (int): Index of the genotype of interest's location
        quantile (float): Quantile for the thresholds calculation
        cmprOp(function): Operation to compare against (less than, greater
            than, etcetera).
    Returns:
        list: Returns the time at which the condition is met at a given
            quantile level.
    """
    prb = srpPrb['landscapes']
    smpNum = len(prb)
    ttiArr = np.empty((smpNum, len(thresholds)))
    for s in range(smpNum):
        refPop = meanRef['population']
        ratioOI = getPopRatio(prb[s], refPop, gIx)
        thsArray = comparePopToThresh(ratioOI, thresholds, cmprOp=op.lt)
        thsDays = thresholdMet(thsArray)
        # Extracting the time to first cross (modify for other metrics)
        ttiArr[s] = [i[0] for i in thsDays]
    quant = np.nanquantile(ttiArr, quantile, axis=0)
    return quant


def calcMeanWOP(meanPrb, meanRef, thresholds, gIx):
    """
    Calculates the mean window of protection for the mean response of two
        populations.
    Args:
        meanPrb (np.array): Mean population of the probe population
        meanRef (np.array): Mean population of the reference population
        thresholds (list): List of ratios to use as thresholds.
        gIx (int): Index of the genotype of interest's location
        cmprOp(function): Operation to compare against (less than, greater
            than, etcetera).
    Returns:
        list: Returns the time at which the condition is met at a given
            quantile level.
    """
    ratioOI = getPopRatio(meanPrb['population'], meanRef['population'], gIx)
    thsArray = comparePopToThresh(ratioOI, thresholds)
    thsDays = thresholdMet(thsArray)
    ttiAn = [len(i) for i in thsDays]
    return ttiAn


def calcQuantWOP(srpPrb, meanRef, thresholds, gIx, quantile=.95):
    """
    Calculates the mean window of protection for the quantile response of two
        populations.
    Args:
        srpPrb (dict): SRP population of the probe population.
        meanRef (np.array): Mean population of the reference population
        thresholds (list): List of ratios to use as thresholds.
        gIx (int): Index of the genotype of interest's location
        quantile (float): Quantile for the thresholds calculation
        cmprOp(function): Operation to compare against (less than, greater
            than, etcetera).
    Returns:
        list: Returns the time at which the condition is met at a given
            quantile level.
    """
    prb = srpPrb['landscapes']
    smpNum = len(prb)
    ttiArr = np.empty((smpNum, len(thresholds)))
    for s in range(smpNum):
        refPop = meanRef['population']
        ratioOI = getPopRatio(prb[s], refPop, gIx)
        thsArray = comparePopToThresh(ratioOI, thresholds, cmprOp=op.lt)
        thsDays = thresholdMet(thsArray)
        ttiArr[s] = [len(i) for i in thsDays]
    quant = np.nanquantile(ttiArr, quantile, axis=0)
    return quant
