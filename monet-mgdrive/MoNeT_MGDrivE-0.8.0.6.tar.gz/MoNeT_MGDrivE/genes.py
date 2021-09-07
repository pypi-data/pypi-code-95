
import re


def countGeneAppearances(genotypes, gene, pos):
    # Split genotypes
    splitGenotypes = [list(genes) for genes in genotypes]
    # Count
    appearances = []
    for p in pos:
        slot = [gene[p] for gene in splitGenotypes]
        matches = re.finditer(gene, ''.join(slot))
        appearances.extend([match.start() for match in matches])
    appearances.sort()
    return appearances


def flatten(ls): return [item for sublist in ls for item in sublist]


def aggregateGeneAppearances(genotypes, genes):
    gcnt = [countGeneAppearances(genotypes, gn[0], gn[1]) for gn in genes]
    return sorted(flatten(gcnt))


def geneFrequencies(genesDict, genotypes):
    gKeys = list(genesDict.keys())
    genes = [genesDict[i] for i in gKeys]
    geneAggs = [aggregateGeneAppearances(genotypes, i) for i in genes]
    return (gKeys, geneAggs)


def carrierFrequencies(genesDict, genotypes, invert=False, autoTotal=True):
    gKeys = list(genesDict.keys())
    genes = [genesDict[i] for i in gKeys]
    (gPos, oPos) = [
        set(aggregateGeneAppearances(genotypes, i)) for i in genes
    ]
    if autoTotal:
        if invert:
            geneSets = [list(i) for i in (gPos - oPos, oPos, gPos | oPos)]
        else:
            geneSets = [list(i) for i in (gPos, oPos - gPos, gPos | oPos)]
        gKeys.append('Total')
    else:
        if invert:
            geneSets = [list(i) for i in (gPos - oPos, oPos)]
        else:
            geneSets = [list(i) for i in (gPos, oPos - gPos)]
    return (gKeys, geneSets)