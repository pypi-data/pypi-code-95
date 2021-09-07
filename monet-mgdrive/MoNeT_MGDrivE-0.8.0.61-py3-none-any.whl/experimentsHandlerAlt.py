from operator import itemgetter
import numpy as np
import warnings as warnings
import MoNeT_MGDrivE.auxiliaryFunctions as auxFun
import MoNeT_MGDrivE.experimentsHandler as expHand


def fileReader(fileName, dtype=float, skipHeader=1, skipColumns=1):
    """
    Description:
        * Loads the data for a single node in the file
            Avoids the use of np.readfromtxt, to avoid the overhead
    In:
        * dataType: To save memory/processing time if possible (int/float).
    Out:
        * Dictionary containing:
            "genotypes" [list -> strings]
            "population" [numpyArray]
    Notes:
        * Timing information is dropped.
    """
    dataFile = open(fileName, 'r')
    headerLen = 0
    for i in range(skipHeader):
        header = next(dataFile)

    rows = []

    if header:
        headerLen = len(header.split(','))
        if headerLen <= skipColumns:
            return np.zeros(1)
    else:
        fline = next(dataFile)
        tokens = fline.split(',')
        headerLen = len(tokens)
        if headerLen <= skipColumns:
            return np.zeros(1)
        rows.append(np.array(tokens[skipColumns:], dtype=dtype))

    # rowLen = headerLen - skipColumns

    previous = [0]*headerLen
    for line in dataFile:
        tokens = line.split(',')
        if len(tokens) != headerLen:
            res = np.array(previous[skipColumns:], dtype=dtype)
        else:
            res = np.array(tokens[skipColumns:], dtype=dtype)
            previous = tokens

        rows.append(res)

    return np.stack(rows)


def loadNodeDataAlt(
    maleFilename=None,
    femaleFilename=None,
    dataType=float,
    skipHeader=1,
    skipColumns=1
):
    """
    Description:
        * Loads the data for a single node in the files. If male and female
            filenames are provided, it sums them as a matrix operation.
            Avoids the use of np.readfromtxt, to avoid the overhead
    In:
        * maleFilename: Path to the male CSV file to process.
        * femaleFilename: Path to the female CSV file to process.
        * dataType: To save memory/processing time if possible (int/float).
    Out:
        * Dictionary containing:
            "genotypes" [list -> strings]
            "population" [numpyArray]
    Notes:
        * Timing information is dropped.
    """
    if (maleFilename is not None) and (femaleFilename is not None):
        genotypes = auxFun.readGenotypes(maleFilename)
        dataM = fileReader(
            maleFilename,
            dtype=dataType,
            skipHeader=skipHeader,
            skipColumns=skipColumns
        )
        dataF = fileReader(
            femaleFilename,
            dtype=dataType,
            skipHeader=skipHeader,
            skipColumns=skipColumns
        )
        if dataM.shape[0] > dataF.shape[0]:
            returnDictionary = {
                "genotypes": genotypes,
                "population": (np.resize(dataM, dataF.shape) + dataF)
            }
        else:
            returnDictionary = {
                "genotypes": genotypes,
                "population": (dataM + np.resize(dataF, dataM.shape))
            }
        return returnDictionary
    elif femaleFilename is not None:
        genotypes = auxFun.readGenotypes(femaleFilename)
        dataF = fileReader(
            femaleFilename,
            dtype=dataType,
            skipHeader=skipHeader,
            skipColumns=skipColumns
        )
        returnDictionary = {
            "genotypes": genotypes,
            "population": dataF
        }
        return returnDictionary
    elif maleFilename is not None:
        genotypes = auxFun.readGenotypes(maleFilename)
        dataM = fileReader(
            maleFilename,
            dtype=dataType,
            skipHeader=skipHeader,
            skipColumns=skipColumns
        )
        returnDictionary = {
            "genotypes": genotypes,
            "population": dataM
        }
        return returnDictionary
    else:
        warnings.warn(
            '''No data was loaded because both male and female filenames
            are: None''',
            Warning
        )
        return None


def loadLandscapeDataAlt(filenames, male=True, female=True, dataType=float):
    """
    Description:
        * Imports the information of all the nodes within an experiment's
            folder.
    In:
        * filenames: Dictionary with male/female filenames.
    Out:
        * Dictionary containing:
            "genotypes" [list -> strings]
            "landscape" [list -> numpyArrays]
    Notes:
        * NA
    """
    maleFilesNumber = len(filenames["male"])
    femaleFilesNumber = len(filenames["female"])
    maleFilesEqualFemales = (maleFilesNumber == femaleFilesNumber)
    filesExist = (maleFilesNumber >= 1 and femaleFilesNumber >= 1)
    # Select the appropriate aggregation scheme: male+female, male, female
    if (male and female) and maleFilesEqualFemales and filesExist:
        maleFilenames = filenames["male"]
        femaleFilenames = filenames["female"]
        genotypes = auxFun.readGenotypes(maleFilenames[0])
        nodesDataList = [None]*maleFilesNumber
        for i in range(0, maleFilesNumber):
            nodesDataList[i] = loadNodeDataAlt(
                maleFilenames[i],
                femaleFilenames[i],
                dataType=dataType
            )["population"]
        returnDictionary = {
            "genotypes": genotypes,
            "landscape": nodesDataList
        }
        return returnDictionary
    elif female and femaleFilesNumber >= 1:
        femaleFilenames = filenames["female"]
        genotypes = auxFun.readGenotypes(femaleFilenames[0])
        nodesDataList = [None] * femaleFilesNumber
        for i in range(0, femaleFilesNumber):
            nodesDataList[i] = loadNodeDataAlt(
                None,
                femaleFilenames[i],
                dataType=dataType
            )["population"]
        returnDictionary = {
            "genotypes": genotypes,
            "landscape": nodesDataList
        }
        return returnDictionary
    elif male and maleFilesNumber >= 1:
        maleFilenames = filenames["male"]
        genotypes = auxFun.readGenotypes(maleFilenames[0])
        nodesDataList = [None] * maleFilesNumber
        for i in range(0, maleFilesNumber):
            nodesDataList[i] = loadNodeDataAlt(
                maleFilenames[i],
                None,
                dataType=dataType
            )["population"]
        returnDictionary = {
            "genotypes": genotypes,
            "landscape": nodesDataList
        }
        return returnDictionary
    else:
        warnings.warn(
            '''No data was loaded because both male and female filenames
                are: None; or there are no files to load.''',
            Warning
        )
        return None


def loadAndAggregateLandscapeDataAlt(
    filenames,
    aggregationDictionary,
    male=True,
    female=True,
    dataType=float
):
    """
    Description:
        * Loads and aggregates the data from a landscape given an aggregation
            dictionary (atomic version of separate operations in previous
            versions)
    In:
        * filenames:
        * aggregationDictionary:
        * male: Boolean to select male files for the aggregation.
        * female: Boolean to select female files for the aggregation.
        * dataType: Data type to save memory/processing time if possible.
    Out:
        * aggLandscape: Aggregated landscape by genotypes.
    Notes:
        * This does not sum the nodes, so the return structure is still an
            array of arrays with the nodes' information (within a dictionary).
    """
    rawLandscape = loadLandscapeDataAlt(
        filenames, male=male, female=female, dataType=dataType
    )
    aggLandscape = expHand.aggregateGenotypesInLandscape(
        rawLandscape,
        aggregationDictionary
    )
    return aggLandscape


def loadAndAggregateLandscapeDataRepetitionsAlt(
    paths,
    aggregationDictionary,
    male=True,
    female=True,
    dataType=float
):
    """
    Description:
        * Loads and aggregates the genotypes of the landscape accross
            repetitions of the same experiment.
    In:
        * paths: Repetitions folders locations.
        * aggregationDictionary: Genotypes and indices counts dictionary.
        * male: Boolean to select male files for the aggregation.
        * female: Boolean to select female files for the aggregation.
        * dataType: Data type to save memory/processing time if possible.
    Out:
        * returnDict: Dictionary with genotypes and the loaded landscapes
            for each one of the repetitions.
    Notes:
        * This function is meant to work with the traces plot, so it has a
            higher dimension (repetitions) than regular spatial analysis
            versions.
    """
    pathsNumber = len(paths)
    landscapes = [None] * pathsNumber
    for i in range(0, pathsNumber):
        filenames = expHand.readExperimentFilenames(paths[i])
        loadedLandscape = loadAndAggregateLandscapeDataAlt(
            filenames, aggregationDictionary,
            male=male, female=female, dataType=dataType
        )
        landscapes[i] = loadedLandscape["landscape"]
    returnDict = {
        "genotypes": aggregationDictionary["genotypes"],
        "landscapes": landscapes
    }
    return returnDict


def sumAggregatedLandscapeDataRepetitionsAlt(
    paths,
    aggregationDictionary,
    male=True,
    female=True,
    dataType=float
):
    """
    Description:
        * Sums the landscape repetitions into one population (effectively
            one node)
    In:
        * landscapeReps: output from loadAndAggregateLandscapeDataRepetitions
    Out:
        * returnDict: Dictionary with genotypes and the loaded landscapes
            for each one of the repetitions.
    Notes:
        * This function is meant to work with the traces plot, by compressing
            landscape repetitions nodes into one population (reducing the
            nodes' dimension)
    """
    repetitions = len(paths)
    reps = [None] * repetitions
    for i in range(repetitions):
        filenames = expHand.readExperimentFilenames(paths[i])
        loadedLandscape = loadAndAggregateLandscapeDataAlt(
            filenames, aggregationDictionary,
            male=male, female=female, dataType=dataType
        )
        minShape = min(
                [x.shape for x in loadedLandscape["landscape"]],
                key=itemgetter(0, 1)
            )
        newSize = [
                np.resize(x, minShape) for x in loadedLandscape["landscape"]
            ]
        reps[i] = [np.sum(newSize, axis=0)]
    returnDict = {
        "genotypes": aggregationDictionary["genotypes"],
        "landscapes": reps
    }

    return returnDict
