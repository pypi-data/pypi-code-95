
import numpy as np


def filterFilesByIndex(files, ix, male=True, female=True):
    '''Given a list of files and an indices list, this function returns the
            nodes contained in the ANALYZED indices list.
    Example: [monet.filterFilesByIndex(files, ix) for ix in NOI]
    Args:
        files (dict): Output from readExperimentFilenames.
        ix (list): List of indices to filter by.
    Returns:
        dict: Filtered nodes in the same form as returned by
                filterFilesByIndex function.
    '''
    m = [files['male'][z] for z in ix] if male else []
    f = [files['female'][z] for z in ix] if female else []
    ffiles = {'male': m, 'female': f}
    return ffiles


def filterGarbageByIndex(landRepetition, indices):
    """
    Args:
        landRepetition (npArray): Landscape data from a node repetiition.
        indices (list): Filtering positions for the nodes of interest.
    Returns:
        list: Nodes' data of the elements contained in the indices list.
    """
    return list(map(landRepetition.__getitem__, indices))


def filterAggregateGarbageByIndex(landscapeReps, indices):
    """Given a list of files and an indices list, this function returns the
            nodes contained in the GARBAGE indices list.
    Args:
        landscapeReps (dict): Output from
            loadAndAggregateLandscapeDataRepetitions
    Returns:
        dict: Filtered nodes in the same form as returned by
                loadAndAggregateLandscapeDataRepetitions function.
    """
    genes = landscapeReps['genotypes']
    repsNumber = len(landscapeReps['landscapes'])
    traces = []
    for j in range(0, repsNumber):
        probe = landscapeReps['landscapes'][j]
        trace = np.sum(filterGarbageByIndex(probe, indices), axis=0)
        traces.append([trace])
    filteredLand = {'genotypes': genes, 'landscapes': traces}
    return filteredLand
