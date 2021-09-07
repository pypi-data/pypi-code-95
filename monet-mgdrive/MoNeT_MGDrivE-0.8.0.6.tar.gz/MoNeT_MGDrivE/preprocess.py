
import compress_pickle as pkl
import MoNeT_MGDrivE.aggregateSpatial as agg
import MoNeT_MGDrivE.experimentsHandler as exp
import MoNeT_MGDrivE.auxiliaryFunctions as aux
import MoNeT_MGDrivE.terminal as ter


def preProcessSubLandscape(
            pop, landReps, fName, drive,
            nodesAggLst, nodeAggIx,
            MF=(True, True), cmpr='bz2',
            SUM=True, AGG=True, SPA=True, REP=True, SRP=True
        ):
    """
    Preprocesses a subset of the landscape
    Args:
        pop (list): Files list element aggregated by landscape subset
        landReps (dict): Landscape repetitions
                (spatial from monet.loadAndAggregateLandscapeDataRepetitions)
        fName (str): Filename (including path)
        drive (dict): Gene-drive dictionary
        nodesAggLst (lst): List of lists containing the indices of the nodes
                to be aggregated together
        nodeAggIx (int): Current list to process (from the nodeAggLst)
        MF (bool tuple): Male and Female boolean selectors
        cmpr (str): Compression algorithm to be used by compress-python
        SUM (bool): Population summed and gene-aggregated into one node
        AGG (bool): Population gene-aggregated in their own nodes
        SPA (bool): Genetic landscape (gene-aggregated)
        REP (bool): Garbage gene-aggregated data
        SRP (bool): Summed into one garbage gene-aggregated data
    Returns:
        None
    """
    if SUM:
        sumData = exp.sumLandscapePopulationsFromFiles(pop, MF[0], MF[1])
        sumAgg = exp.aggregateGenotypesInNode(sumData, drive)
        pkl.dump(sumAgg, fName+'_sum', compression=cmpr)
    if AGG:
        aggData = exp.loadAndAggregateLandscapeData(pop, drive, MF[0], MF[1])
        pkl.dump(aggData, fName+'_agg', compression=cmpr)
    if SPA:
        geneSpaTemp = exp.getGenotypeArraysFromLandscape(aggData)
        pkl.dump(geneSpaTemp, fName+'_spa', compression=cmpr)
    if REP or SRP:
        fLandReps = agg.filterAggregateGarbageByIndex(
                landReps, nodesAggLst[nodeAggIx]
            )
        if REP:
            pkl.dump(fLandReps, fName+'_rep', compression=cmpr)
    if SRP:
        fRepsSum = [sum(i) for i in fLandReps['landscapes']]
        fRepsDict = {
                'genotypes': fLandReps['genotypes'],
                'landscapes': fRepsSum
            }
        pkl.dump(fRepsDict, fName+'_srp', compression=cmpr)
    return None


def preProcessLandscape(
            pathMean, pathTraces, expName, drive, prePath='./',
            nodesAggLst=[[0]], analysisOI='HLT', fNameFmt='{}/{}-{}_',
            MF=(True, True), cmpr='bz2', nodeDigits=4,
            SUM=True, AGG=True, SPA=True, REP=True, SRP=True,
            sexFilenameIdentifiers={"male": "M_", "female": "F_"}
        ):
    """
    Preprocesses a subset of the landscape
    Args:
        pathMean (str): Files list element aggregated by landscape subset
        pathTraces (str): Landscape repetitions
                (spatial from monet.loadAndAggregateLandscapeDataRepetitions)
        expName (str): Filename (including path)
        drive (dict): Gene-drive dictionary
        prePath (str): Preprocess path for export
        nodesAggLst (int): Current list to process (from the nodeAggLst)
        analysisOI (str): ID for type of analysis (HLT or ECO for now)
        fNameFmt (str): Format string for the experiments (prePath+expName+AOI)
        MF (bool tuple): Male and Female boolean selectors
        nodeDigits
        cmpr (str): Compression algorithm to be used by compress-python
        SUM (bool): Population summed and gene-aggregated into one node
        AGG (bool): Population gene-aggregated in their own nodes
        SPA (bool): Genetic landscape (gene-aggregated)
        REP (bool): Garbage gene-aggregated data
        SRP (bool): Summed into one garbage gene-aggregated data
    Returns:
        None
    """
    dirsTraces = aux.listDirectoriesWithPathWithinAPath(pathTraces)
    files = exp.readExperimentFilenames(
        pathMean, sexFilenameIdentifiers=sexFilenameIdentifiers
    )
    filesList = [agg.filterFilesByIndex(files, ix) for ix in nodesAggLst]
    landReps = None
    if REP or SRP:
        landReps = exp.loadAndAggregateLandscapeDataRepetitions(
                dirsTraces, drive, MF[0], MF[1],
                sexFilenameIdentifiers=sexFilenameIdentifiers
            )
    for (nodeAggIx, pop) in enumerate(filesList):
        fName = fNameFmt + str(nodeAggIx).zfill(nodeDigits)
        preProcessSubLandscape(
                    pop, landReps, fName, drive,
                    nodesAggLst, nodeAggIx,
                    MF=MF, cmpr=cmpr,
                    SUM=SUM, AGG=AGG, SPA=SPA, REP=REP, SRP=SRP,
                )
    return None


def preProcess(
            exIx, expNum, expDirsMean, expDirsTrac,
            drive, analysisOI='HLT', prePath='./',
            nodesAggLst=[[0]], outExpNames={},
            fNameFmt='{}/{}-{}_', OVW=True,
            MF=(True, True), cmpr='bz2', nodeDigits=4,
            SUM=True, AGG=False, SPA=False, REP=False, SRP=True,
            sexFilenameIdentifiers={"male": "M_", "female": "F_"}
        ):
    """
    Preprocesses a subset of the landscape
    Args:
        exIx (str): Files list element aggregated by landscape subset
        expNum (str):
        expDirsMean (str): Path to the ANALYZED folder
        expDirsTrac (str): Path to the GARBAGE folder
        drive (dict): Gene-drive dictionary
        analysisOI (str): ID for type of analysis (HLT or ECO for now)
        prePath (str): Preprocess path for export
        outExpNames (set): Experiments names already preprocessed
        nodesAggLst (int): Current list to process (from the nodeAggLst)
        fNameFmt (str): Format string for the experiments (prePath+expName+AOI)
        MF (bool tuple): Male and Female boolean selectors
        nodeDigits (int): Number of digits to be used for nodes padding
        OVW (bool): Overwrite existing experiments (in outExpNames)
        cmpr (str): Compression algorithm to be used by compress-python
        SUM (bool): Population summed and gene-aggregated into one node
        AGG (bool): Population gene-aggregated in their own nodes
        SPA (bool): Genetic landscape (gene-aggregated)
        REP (bool): Garbage gene-aggregated data
        SRP (bool): Summed into one garbage gene-aggregated data
    Returns:
        None
    """
    # Setup paths -------------------------------------------------------------
    ter.printProgress(exIx+1, expNum, nodeDigits)
    (pathMean, pathTraces) = (expDirsMean[exIx], expDirsTrac[exIx]+'/')
    expName = pathMean.split('/')[-1]
    if (OVW) or (not (expName in outExpNames)):
        fNameFmt = '{}/{}-{}_'.format(prePath, expName, analysisOI)
        preProcessLandscape(
                    pathMean, pathTraces, expName, drive, prePath,
                    analysisOI=analysisOI, nodesAggLst=nodesAggLst,
                    fNameFmt=fNameFmt, MF=MF, cmpr=cmpr, nodeDigits=nodeDigits,
                    SUM=SUM, AGG=AGG, SPA=SPA, REP=REP, SRP=SRP,
                    sexFilenameIdentifiers=sexFilenameIdentifiers
                )
    return None
