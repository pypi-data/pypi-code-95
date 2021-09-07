import math
import numpy as np
import scipy.stats as stats
import itertools
# import vincenty as vn

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Constants
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
AEDES_EXP_PARAMS = [0.01848777, 1.0e-10, math.inf]


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Kernels
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def normalizeKernel(kernel):
    '''
    Takes a numpy array in, and returns a row-wise normalized copy.
    '''
    kernelOut = np.empty(kernel.shape)
    for (i, row) in enumerate(kernel):
        kernelOut[i] = row/np.sum(row)
    return kernelOut


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Distances
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def euclideanDistance(a, b):
    '''
    Calculates the Euclidean distance between two-dimensional coordinates.
    '''
    dist = math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)
    return dist


def calculateDistanceMatrix(landscape, distFun=euclideanDistance):
    '''
    Returns the distance matrix according to the provided distance function.
        Examples of these are: euclideanDistance (xy), vn.vincenty (latlong).
    '''
    coordsNum = len(landscape)
    distMatrix = np.empty((coordsNum, coordsNum))
    for (i, coordA) in enumerate(landscape):
        for (j, coordB) in enumerate(landscape):
            distMatrix[i][j] = distFun(coordA, coordB)
    return distMatrix


def sortByDistanceToPOI(poi, landscape, distFun=euclideanDistance):
    '''
    Returns a numpy array of sorted coordinates according to the distance
        to an arbitrary point of interest (POI).
    NOTE: Make sure the landscape & POI are in latlong form! The output is
        returned in longlat format.
    '''
    # Compute distances to POI
    latlongs = np.asarray(landscape)
    distances = [distFun(poi, (row[1], row[0])) for row in latlongs]
    # Get the sorting of the distances and concatenate to longlats
    sorting = np.asarray(distances).argsort()
    distArray = np.asarray([distances])
    longlatDist = np.concatenate((latlongs, distArray.T), axis=1)
    # Apply the sorting and return the array
    longlatDistSort = longlatDist[sorting]
    return longlatDistSort


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#  Linear Kernel Functions
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def inverseLinearStep(distance, params=[.75, 1]):
    '''
    Returns a migration estimate based on the inverse of the
        distance. NOTE: This is a terrible way to do it, but it's a first
        approximation. Should be replaced with the zero-inflated exponential.
    '''
    if math.isclose(distance, 0):
        return params[0]
    else:
        return (1 / (distance * params[1]))
    return True


def zeroInflatedLinearMigrationKernel(
            distMat,
            params=[.75, 1]
        ):
    '''
    Takes in the distances matrix, zero inflated value (step) and two extra
        parameters to determine the change from distances into distance-based
        migration probabilities (based on the kernel function provided).
    '''
    coordsNum = len(distMat)
    migrMat = np.empty((coordsNum, coordsNum))
    for (i, row) in enumerate(distMat):
        for (j, dst) in enumerate(row):
            migrMat[i][j] = inverseLinearStep(dst, params=params)
        # Normalize rows to sum 1
        migrMat[i] = migrMat[i] / sum(migrMat[i])
    return migrMat


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Exponential Migration Kernels
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def truncatedExponential(distance, params=AEDES_EXP_PARAMS):
    '''
    Calculates the zero-inflated exponential for the mosquito movement kernel
        (default parameters set to Aedes aegypti calibrations).

        params = [rate, a, b]
    '''
    if(params[1] > params[2]):
        return None

    scale = 1.0/params[0]
    gA = stats.expon.cdf(params[1], scale=scale)
    gB = stats.expon.cdf(params[2], scale=scale)
    if np.isclose(gA, gB):
        return None

    densNum = stats.expon.pdf(distance, scale=scale)
    densDen = gB - gA

    return densNum/densDen


def zeroInflatedExponentialMigrationKernel(
            distMat,
            params=AEDES_EXP_PARAMS,
            zeroInflation=.75
        ):
    '''
    Calculates the migration matrix using a zero-inflated exponential function
        taking as arguments the species-specific lifespan parameters, and the
        kernel constants (along with the lifelong stay probability).
    '''
    coordsNum = len(distMat)
    migrMat = np.empty((coordsNum, coordsNum))
    for (i, row) in enumerate(distMat):
        for (j, dst) in enumerate(row):
            if(i == j):
                migrMat[i][j] = 0
            else:
                migrMat[i][j] = truncatedExponential(dst, params=params)
        migrMat[i] = migrMat[i] / np.sum(migrMat[i]) * (1 - zeroInflation)
    np.fill_diagonal(migrMat, zeroInflation)
    return migrMat


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Kernel Aggregation
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def aggregateLandscape(migrationMatrix, clusters, type=0):
    '''
    Takes the migration matrix, and the clusters list and performs the Markov
        aggregation of the landscape.
    '''
    if type == 0:
        return aggregateLandscapeBase(migrationMatrix, clusters)
    elif type == 1:
        return aggregateLandscapeAltGill(migrationMatrix, clusters)
    elif type == 2:
        return aggregateLandscapeAltVic(migrationMatrix, clusters)


def aggregateLandscapeBase(migrationMatrix, clusters):
    '''
    Takes the migration matrix, and the clusters list and performs the Markov
        aggregation of the landscape.
    '''
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_latlongs = [[] for x in range(num_clusters)]
    for idx, label in enumerate(clusters):
        aggr_latlongs[label].append(idx)
    for row in range(num_clusters):
        row_ids = aggr_latlongs[row]
        for colum in range(num_clusters):
            colum_ids = aggr_latlongs[colum]
            res = 0
            for rid in row_ids:
                for cid in colum_ids:
                    res += migrationMatrix[rid][cid]
            aggr_matrix[row][colum] = res/len(row_ids)
    return aggr_matrix


def aggregateLandscapeAltVic(migrationMatrix, clusters):
    '''
    Faster version of the aggregation algorithm dev by Gillian
    '''
    matrix_size = len(clusters)
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_number = [0]*num_clusters
    for row in range(matrix_size):
        cRow = clusters[row]
        aggr_number[cRow] += 1
        for col in range(matrix_size):
            cCol = clusters[col]
            aggr_matrix[cRow][cCol] += migrationMatrix[row][col]
    for row in range(num_clusters):
        aggr_matrix[row] = [x/aggr_number[row] for x in aggr_matrix[row]]
    return aggr_matrix


def aggregateLandscapeAltGill(migrationMatrix, clusters):
    '''
    Another alternative of the aggregation algorithm dev by Gillian
    '''
    num_clusters = len(set(clusters))
    aggr_matrix = np.zeros([num_clusters, num_clusters], dtype=float)
    aggr_latlongs = [[] for x in range(num_clusters)]
    # get all the patches that fall under each label
    [aggr_latlongs[label].append(idx) for idx, label in enumerate(clusters)]
    # get the number of patches in each label for normalization later
    normVal = dict()
    for idx, label in enumerate(clusters):
        normVal[label] = len(aggr_latlongs[label])
    for row in range(num_clusters):
        row_ids = aggr_latlongs[row]
        for column in range(num_clusters):
            colum_ids = aggr_latlongs[column]
            all_comb = [
                migrationMatrix[x][y] for (x, y) in [itertools.product([row_ids, colum_ids])]
            ]
            aggr_matrix[row][column] = sum(all_comb)/len(row_ids)
    return aggr_matrix
