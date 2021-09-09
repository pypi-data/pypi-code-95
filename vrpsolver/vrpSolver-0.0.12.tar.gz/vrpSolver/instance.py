import random
import math
import tripy

from .msg import *
from .common import *

def rndPlainNodes(
    N:          "Number of vertices" = None,
    nodeIDs:    "A list of node IDs, `N` will be overwritten if `nodeIDs` is given" = None,
    poly:       "Nodes will be generated within the given polygon, will overwrite `xRange` and `yRange`. \
                 If `poly` is not provided, nodes will be created in a square." = None,
    xRange:     "A 2-tuple with minimum/maximum range of x" = (0, 100),
    yRange:     "A 2-tuple with minimum/maximum range of y" = (0, 100),
    ) -> "A set of nodes with id start from 0 to N":

    # Check for required fields ===============================================
    if (N == None):
        print(ERROR_MISSING_N)
        return

    # Initialize ==============================================================
    nodes = {}
    if (nodeIDs == None):
        nodeIDs = [i for i in range(N)]

    # Generate instance
    if (poly == None):
        for i in nodeIDs: 
            x = random.randrange(xRange[0], xRange[1])
            y = random.randrange(yRange[0], yRange[1])
            nodes[i] = {'loc': (x, y)}
    else:
        # FIXME: Using `tripy` package for now, will rewrite the functionality
        lstTriangle = tripy.earclip(poly)
        lstWeight = []
        for i in range(len(lstTriangle)):
            lstWeight.append(calTriangleAreaByCoords(lstTriangle[i][0], lstTriangle[i][1], lstTriangle[i][2]))
        for n in nodeIDs:
            idx = rndPick(lstWeight)
            [x1, y1] = lstTriangle[idx][0]
            [x2, y2] = lstTriangle[idx][1]
            [x3, y3] = lstTriangle[idx][2]
            rndR1 = np.random.uniform(0, 1)
            rndR2 = np.random.uniform(0, 1)
            rndX = (1 - math.sqrt(rndR1)) * x1 + math.sqrt(rndR1) * (1 - rndR2) * x2 + math.sqrt(rndR1) * rndR2 * x3
            rndY = (1 - math.sqrt(rndR1)) * y1 + math.sqrt(rndR1) * (1 - rndR2) * y2 + math.sqrt(rndR1) * rndR2 * y3
            nodes[n] = {'loc': (rndX, rndY)}

    return nodes


def _genNodesUniformBounded(numNodes=None, boundingRegion=None):
    """
    Generate randomized node using Uniform distribution within a bounding area

    Note
    ----
    This function is an approximation, the error is getting larger when the location is closer to poles

    Parameters
    ----------
    numNodes: int, Required
        Number of nodes to be generated
    boudingArea: list, Required
        A defined polygon, nodes are generated within this area

    Returns
    -------
    list of lists
        A list of coordinates uniformly distributed with bounding region
    """

    # Use polygon triangulation to cut the bounding region into a list of triangules, calculate the area of each triangle

    
    # Randomly pick a triangle, the probability of picking triangle is refer to the area of each triangle, then generate one node inside, loop untill generate enough nodes
    locs = []
    for i in range(numNodes):
        index = randomPick(lstArea)
        newLoc = _genNodesUniformTriangle(1, lstTriangle[index])
        locs.extend(newLoc)

    return locs

def _genNodesUniformTriangle(numNodes=None, triangle=None):
    # Give number to three vertices of triangle
    [lat1, lon1] = triangle[0]
    [lat2, lon2] = triangle[1]
    [lat3, lon3] = triangle[2]

    # initialize lists
    locs = []
    # Generate random nodes
    # Reference: http://www.cs.princeton.edu/~funk/tog02.pdf
    for i in range(numNodes):
        rndR1 = np.random.uniform(0, 1)
        rndR2 = np.random.uniform(0, 1)
        rndLat = (1 - math.sqrt(rndR1)) * lat1 + math.sqrt(rndR1) * (1 - rndR2) * lat2 + math.sqrt(rndR1) * rndR2 * lat3
        rndLon = (1 - math.sqrt(rndR1)) * lon1 + math.sqrt(rndR1) * (1 - rndR2) * lon2 + math.sqrt(rndR1) * rndR2 * lon3
        locs.append([rndLat, rndLon])

    return locs

def rndTimeWindowsNodes(
    N:          "Number of vertices" = None,
    nodes:      "If nodes are provided, will overwrite `nodeIDs`, `xRange`, `yRange`, time windows will be applied on those nodes" = None,
    nodeIDs:    "A list of node IDs, `N` will be overwritten if `nodeIDs` is given" = None,
    xRange:     "A 2-tuple with minimum/maximum range of x" = (0, 100),
    yRange:     "A 2-tuple with minimum/maximum range of y" = (0, 100),
    timeSpan:   "Time span for generating time windows, starting from 0" = None,
    twType:     "Type of time windows\
                 1) String 'Known', all time windows are given priorly, or \
                 2) String 'Periodic', time windows are generated periodically, or \
                 3) String 'Random', time windows are generated randomly " = 'Random',
    twArgs:     "Dictionary, \
                 1) For 'Known' twType:\
                    {\
                        'timeWindows': A list of 2-tuples, e.g., [(s1, e1), (s2, e2), ...]\
                    }\
                 2) For 'Periodic' twType:\
                    {\
                        'cycleTime': cycleTime, \
                        'startTimeInCycle': startTimeInCycle, \
                        'endTimeInCycle': endTimeInCycle \
                    }\
                 3) For 'Random' twType:\
                    {\
                        'indFlag': True if different nodes have different time windows, False otherwise,\
                        'avgBtwDur': average interval time between time windows, exponential distributed,\
                        'avgTWDur': average length of time windows, exponential distributed\
                    }" = None
    ) -> "A set of nodes with time windows":

    # Check for required fields ===============================================
    if (N == None and nodes == None):
        print(ERROR_MISSING_N)
        return
    if (timeSpan == None):
        print(ERROR_MISSING_TIMESPAN)
        return
    validTWOpts = ['Known', 'Periodic', 'Random']
    if (twType not in validTWOpts):
        print(ERROR_OPTS_TWTYPE % validTWOpts)
        return
    elif (twType == 'Known'):
        if (twArgs == None):
            print(ERROR_MISSING_TWKNOWNARGS)
            return
        elif ('timeWindows' not in twArgs):
            print (ERROR_MISSING_TWKNOWNARGS_TW)
            return
    elif (twType == 'Periodic'):
        if (twArgs == None):
            print(ERROR_MISSING_TWPERIODICARGS)
            return
        elif ('cycleTime' not in twArgs):
            print(ERROR_MISSING_TWPERIODICARGS_CT)
            return
        elif ('startTimeInCycle' not in twArgs):
            print(ERROR_MISSING_TWPERIODICARGS_ST)
            return
        elif ('endTimeInCycle' not in twArgs):
            print(ERROR_MISSING_TWPERIODICARGS_ET)
            return
    elif (twType == 'Random'):
        if (twArgs == None):
            print(ERROR_MISSING_TWRANDOMARGS)
            return
        elif ('indFlag' not in twArgs):
            print(ERROR_MISSING_TWRANDOMARGS_FG)
            return
        elif ('avgBtwDur' not in twArgs):
            print(ERROR_MISSING_TWRANDOMARGS_BTW)
            return
        elif ('avgTWDur' not in twArgs):
            print(ERROR_MISSING_TWRANDOMARGS_TW)
            return

    # Initialize nodes ========================================================
    if (nodes == None):
        nodes = rndPlainNodes(N, nodeIDs, xRange, yRange)

    # Generate time windows for different types ===============================
    for n in nodes:
        nodes[n]['timeWindows'] = []
    if (twType == "Known"):
        for n in nodes:
            nodes[n]['timeWindows'] = twArgs['timeWindows']
    elif (twType == 'Periodic'):
        repeatNum = math.ceil(timeSpan / twArgs['cycleTime'])
        for tw in range(repeatNum):
            for n in nodes:
                nodes[n]['timeWindows'].append((
                    tw * twArgs['cycleTime'] + twArgs['startTimeInCycle'], 
                    tw * twArgs['cycleTime'] + twArgs['endTimeInCycle']))
    elif (twType == 'Random'):
        avgBtwDur = twArgs['avgBtwDur']
        avgTWDur = twArgs['avgTWDur']
        # If all nodes have different time windows
        if (twArgs['indFlag'] == False):
            now = 0
            pre = 0
            availFlag = True if (random.random() < (avgTWDur / (avgTWDur + avgBtwDur))) else False
            while (now < timeSpan):            
                interval = 0
                if (availFlag):
                    if (avgTWDur > 0):
                        interval = random.expovariate(1 / avgTWDur)
                        now += interval
                        if (interval > 0.0001):
                            for n in nodes:
                                nodes[n]['timeWindows'].append((pre, now))
                else:
                    if (avgBtwDur > 0):
                        interval = random.expovariate(1 / avgBtwDur)
                        now += interval
                availFlag = not availFlag
                pre = now
        # If all nodes have the same time windows
        else:
            for n in nodes:
                now = 0
                pre = 0
                availFlag = True if (random.random() < (avgTWDur / (avgTWDur + avgBtwDur))) else False
                while (now < timeSpan):
                    interval = 0
                    if (availFlag):
                        if (avgTWDur > 0):
                            interval = random.expovariate(1 / avgTWDur)
                            now += interval
                            if (interval > 0.0001):
                                nodes[n]['timeWindows'].append((pre, now))
                    else:
                        if (avgBtwDur > 0):
                            interval = random.expovariate(1 / avgBtwDur)
                            now += interval
                    availFlag = not availFlag
                    pre = now

    # Truncate last time window to fit time span ==============================
    for n in nodes:
        while (len(nodes[n]['timeWindows']) > 0 and (nodes[n]['timeWindows'][-1][0] >= timeSpan or nodes[n]['timeWindows'][-1][1] > timeSpan)):
            lastStart = nodes[n]['timeWindows'][-1][0]
            if (lastStart >= timeSpan):
                for n in nodes:
                    nodes[n]['timeWindows'] = nodes[n]['timeWindows'][:-1]
            lastEnd = nodes[n]['timeWindows'][-1][1]
            if (lastEnd >= timeSpan):
                for n in nodes:
                    nodes[n]['timeWindows'][-1] = (
                        nodes[n]['timeWindows'][-1][0], 
                        timeSpan)

    return nodes