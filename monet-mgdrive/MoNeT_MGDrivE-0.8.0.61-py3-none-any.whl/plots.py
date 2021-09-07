import numpy as np
import pandas as pd
from os import path
import compress_pickle as pkl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import MoNeT_MGDrivE.colors as monetPlots
import MoNeT_MGDrivE.terminal as ter
import MoNeT_MGDrivE.auxiliaryFunctions as auxFun
import MoNeT_MGDrivE.experimentsHandler as expHan
import MoNeT_MGDrivE.dataAnalysis as dataA

def rescaleRGBA(colorsTuple, colors=255):
    """
    Description:
        * Rescales a 0-255 color to 0-1
    In:
        * Color RGB tuple/list in 8bit
    Out:
        * Color RGB tuple in 0-1
    Notes:
        * NA
    """
    return [i/colors for i in colorsTuple]


def plotNodeTracesOnFigure(
    landscapeReps,
    style,
    figure
):
    """
    Description:
        * Generates the individual "traces" plot for a whole landscape
            iteratively.
    In:
        * landscapeReps: landscape repetitions data generated with
            loadAndAggregateLandscapeDataRepetitions.
        * style: styling options for the plot.
        * fig: figure to plot on top of.
    Out:
        * fig: a matplotlib traces figure with all of the information on the
            landscapeReps.
    Notes:
        * NA
    """
    # repetitions = len(landscapeReps["landscapes"])
    # nodesNumb = len(landscapeReps["landscapes"][0])
    genesNumber = len(landscapeReps["landscapes"][0][0][0])

    if not figure:
        fig, ax = plt.subplots()
    else:
        fig = figure
        ax = figure.get_axes()[0]

    for rep in landscapeReps["landscapes"]:
        for node in rep:
            transposed = node.T
            for gene in range(0, genesNumber):
                ax.plot(
                    transposed[gene],
                    linewidth=style["width"],
                    color=style["colors"][gene]
                )

    return fig


def plotMeanGenotypeTrace(aggData, style):
    """
    Description:
        * Plots the mean response of an aggregate dataset.
    In:
        * aggData: dictionary containing "genotype" and "populations" pairs
        * style: dictionary containing width, colors, aspect, alpha
    Out:
        * fig: matplotlib figure
    Notes:
        * NA
    """
    groups = aggData['genotypes']
    pops = aggData['population']
    time = np.arange(len(pops))
    df = pd.DataFrame(time, columns=['Time'])
    final = [df[['Time']] for _ in range(len(groups))]
    local = pd.DataFrame(pops, columns=groups)
    fig, ax = plt.subplots()
    ax.set_aspect(aspect=style["aspect"])
    # plt.xticks([])
    # plt.yticks([])
    for j in range(len(groups)):
        final[j].insert(1, groups[j] + str(1), (local[groups[j]]).copy())
        final[j] = final[j].set_index('Time')
    for i in range(len(final)):
        final[i].plot(
            ax=ax, linewidth=style["width"], legend=False,
            color=style["colors"][i]
        )
    legends = []
    for i in range(len(groups)):
        legends.append(
            mpatches.Patch(color=style["colors"][i], label=groups[i])
        )
    if style["legend"] is True:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2,
                   ncol=2, borderaxespad=0.)
    ax.xaxis.set_label_text("")
    ax.yaxis.set_label_text("")
    # plt.ylabel("Allele Count")
    return fig


def plotMeanGenotypeStack(
    aggData,
    style,
    vLinesCoords=[]
):
    """
    Description:
        * Plots the mean response of an aggregate dataset.
    In:
        * aggData: dictionary containing "genotype" and "populations" pairs
        * style: dictionary containing width, colors, aspect, alpha
    Out:
        * fig: matplotlib figure
    Notes:
        * NA
    """
    groups = aggData['genotypes']
    pops = aggData['population']
    time = np.arange(len(pops))
    df = pd.DataFrame(time, columns=['Time'])
    final = [df[['Time']] for _ in range(len(groups))]
    local = pd.DataFrame(pops, columns=groups)
    fig, ax2 = plt.subplots()
    ax2.set_aspect(aspect=style["aspect"])
    allele_dict = {}
    for j in range(len(groups)):
        final[j].insert(1, groups[j] + str(1), (local[groups[j]]).copy())
        final[j] = final[j].set_index('Time')
    for i in range(len(groups)):
        allele_dict[groups[i]] = final[i].T.sum()
    res = pd.DataFrame(allele_dict)
    res = res.reindex(columns=groups)
    res.plot(
        kind='area', ax=ax2, legend=style["legend"], color=style["colors"],
        linewidth=style["width"], alpha=style["alpha"]
    )
    for i in range(len(vLinesCoords)):
        ax2.plot(
            [vLinesCoords[i], vLinesCoords[i]],
            [style["yRange"][0], style["yRange"][1]],
            'k--',
            lw=.25
        )
    plt.ylabel("")
    plt.xlabel("")
    if style["legend"] is True:
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2,
                   ncol=2,  borderaxespad=0.)
    return fig


def plotGenotypeFromLandscape(
    landscapeGene,
    style={"aspect": 12, "cmap": monetPlots.cmaps[0]}
):
    """
    Description:
        * Creates the heatmap plot of a gene array
    In:
        * landscapeGene: spatiotemporal array for the gene to plot
        * style: styling options for the plot
    Out:
        * fig: matplotlib figure
    Notes:
        * NA
    """
    fig, ax = plt.subplots(nrows=1, figsize=(20, 5))
    ax.imshow(landscapeGene, cmap=style["cmap"], aspect=style["aspect"])
    return fig


def plotGenotypeArrayFromLandscape(
    geneSpatiotemporals,
    style={"aspect": 12, "cmap": monetPlots.cmaps}
):
    """
    Description:
        * Creates the heatmap plot of all the genotypes in the landscape
            separately.
    In:
        * landscapeData: population dynamics data
        * style: styling options for the plot
    Out:
        * fig: matplotlib figure
    Notes:
        * NA
    """
    genesNumber = len(geneSpatiotemporals["genotypes"])
    plotsList = [None] * genesNumber
    for i in range(0, genesNumber):
        plotsList[i] = plotGenotypeFromLandscape(
            geneSpatiotemporals["geneLandscape"][i],
            style={"aspect": style["aspect"], "cmap": style["cmap"][i]}
        )
    plotsDict = {
        "genotypes": geneSpatiotemporals["genotypes"],
        "plots": plotsList
    }
    return plotsDict


def plotGenotypeOverlayFromLandscape(
    geneSpatiotemporals,
    style={"aspect": 12, "cmap": monetPlots.cmaps},
    vmin=None,
    vmax=None
):
    """
    Description:
        * Plots the combined "landscape-heatmap" plots in one.
    In:
        * geneSpatiotemporals: Array of the spatiotemporal genotypes
            information (gene counts across nodes through time).
        * style: styling options for the plot
        * vmin:
        * vmax:
    Out:
        * fig: matplot fig of combined heatmaps
    Notes:
        * NA
    """
    alleleNames = geneSpatiotemporals["genotypes"]
    counts = geneSpatiotemporals["geneLandscape"]
    fig = plt.figure(figsize=(20, 5))
    for i in range(len(alleleNames)):
        plt.imshow(
            counts[i],
            cmap=style["cmap"][i],
            aspect=style["aspect"],
            vmin=vmin, vmax=vmax
        )
    return fig


def plotNodeDataRepetitions(
    nodeRepetitionsArray,
    style
):
    """
    Description:
        * Generates the "traces" plot for one node.
    In:
        * nodeRepetitionsArray: Intermediate structure generated by taking
            the information of a given node accross all landscapes.
        * style: styling options for the plot
    Out:
        * fig: matplotlib traces figure
    Notes:
        * This function is meant to work within plotLandscapeDataRepetitions,
            so it's not necessary to call it directly.
    """
    probeNode = nodeRepetitionsArray
    repsNumber = len(probeNode)
    genesNumber = len(probeNode[0][0])
    fig, ax = plt.subplots()
    ax.set_aspect(aspect=style["aspect"])
    for j in range(0, repsNumber):
        transposed = probeNode[j].T
        for gene in range(0, genesNumber):
            ax.plot(
                transposed[gene],
                linewidth=style["width"],
                color=style["colors"][gene]
            )
    return fig


def plotNodeTraces(
    srpData,
    style
):
    """
    Description:
        * Generates the "traces" plot for one node.
    In:
        * srpData: Intermediate structure generated by taking
            the information of a given node accross all landscapes.
        * style: styling options for the plot
    Out:
        * fig: matplotlib traces figure
    Notes:
        * This function is meant to work within plotLandscapeDataRepetitions,
            so it's not necessary to call it directly.
    """
    probeNode = srpData['landscapes']
    repsNumber = len(probeNode)
    genesNumber = len(probeNode[0][0])
    fig, ax = plt.subplots()
    ax.set_aspect(aspect=style["aspect"])
    for j in range(0, repsNumber):
        transposed = probeNode[j].T
        for gene in range(0, genesNumber):
            ax.plot(
                transposed[gene],
                linewidth=style["width"],
                color=style["colors"][gene]
            )
    return (fig, ax)


def plotLandscapeDataRepetitions(
    landscapeReps,
    style
):
    """
    Description:
        * Generates the individual "traces" plots for a whole landscape.
    In:
        * landscapeReps: landscape repetitions data generated with
            loadAndAggregateLandscapeDataRepetitions.
        * style: styling options for the plot.
    Out:
        * figs: array of matplotlib traces figures.
    Notes:
        * NA
    """
    landscapes = landscapeReps["landscapes"]
    landscapesNumb = len(landscapeReps["landscapes"][0])
    figs = [None] * landscapesNumb
    for i in range(0, landscapesNumb):
        probeNode = list(zip(*landscapes))[i]
        figs[i] = plotNodeDataRepetitions(probeNode, style)
    return figs


def plotAllTraces(
    landscapeReps,
    style
):
    """
    Description:
        * Generates the individual "traces" plot for a whole landscape.
    In:
        * landscapeReps: landscape repetitions data generated with
            loadAndAggregateLandscapeDataRepetitions.
        * style: styling options for the plot.
    Out:
        * fig: a matplotlib traces figure with all of the information on the
            landscapeReps.
    Notes:
        * NA
    """
    # repetitions = len(landscapeReps["landscapes"])
    # nodesNumb = len(landscapeReps["landscapes"][0])
    genesNumber = len(landscapeReps["landscapes"][0][0][0])
    fig, ax = plt.subplots()
    ax.set_aspect(aspect=style["aspect"])
    for rep in landscapeReps["landscapes"]:
        for node in rep:
            transposed = node.T
            for gene in range(0, genesNumber):
                ax.plot(
                    transposed[gene],
                    linewidth=style["width"],
                    color=style["colors"][gene]
                )

    return fig


def quickSaveFigure(
    fig,
    path,
    dpi=1024,
    format="png"
):
    """
    Description:
        * Standardized method to save experiments figures.
    In:
        * fig: figure to save
        * path: directory to save to
        * dpi: resolution
        * format: image format
    Out:
        * NA: (saves to disk)
    Notes:
        * NA
    """
    fig.savefig(
        path, dpi=dpi, facecolor=None,
        orientation='portrait', 
        format=format, transparent=True, bbox_inches='tight',
        pad_inches=0
    )


def scaleAspect(aspect, style):
    """
    Description:
        * Helper function to override the aspect ratio value on the ranges
            in a more meaningful way.
    In:
        * aspect: float parameter to scale the x/y ratio on the plots
        * style: dictionary with style components for the plot
    Out:
        * float: Scaling factor for the plot
    Notes:
        * Example: style['aspect'] = scaleAspect(.2, style)
    """
    xDiff = (style['xRange'][1] - style['xRange'][0])
    yDiff = (style['yRange'][1] - style['yRange'][0])
    return aspect * (xDiff / yDiff)


def exportLegend(legend, filename="legend.png", dpi=500):
    """Helper function to draw a palette legend independent from the plot.

    Parameters
    ----------
    legend : plt
        Plt object of handles and labels.
    filename : str
        Path to store the legend file in.
    dpi : int
        Resolution of the legend.

    Returns
    -------
    type
        NA

    """
    fig = legend.figure
    fig.canvas.draw()
    bbox = legend.get_window_extent().transformed(
            fig.dpi_scale_trans.inverted()
        )
    fig.savefig(filename, dpi=dpi, bbox_inches=bbox)
    plt.clf()
    plt.cla() 
    plt.close('all')
    plt.gcf()
    return None


def exportGeneLegend(labels, colors, filename, dpi):
    """Generates a gene-labels legend to a file.

    Parameters
    ----------
    labels : strings list
        List of strings to use as legend names (genes).
    colors : colors list
        List of colors for the swatch.
    filename : string path
        Path to store the legend file in.
    dpi : integer
        Resolution of the legend

    Returns
    -------
    type
        NA

    """
    def f(m, c): return plt.plot([], [], marker=m, color=c, ls="none")[0]
    handles = [f("s", colors[i]) for i in range(len(labels))]
    legend = plt.legend(handles, labels, loc=3, framealpha=1, frameon=False)
    exportLegend(legend, filename=filename, dpi=dpi)
    plt.clf()
    plt.cla() 
    plt.close('all')
    plt.gcf()
    return None



def exportTracesPlot(
    tS, nS, STYLE, PATH_IMG, append='', 
    vLines=[0, 0], hLines=[0], labelPos=(.7, .95), autoAspect=False,
    border=True, borderColor='#8184a7AA', borderWidth=2, popScaler=1,
    wop=0, wopPrint=True, 
    cpt=0, cptPrint=False, 
    poe=0, poePrint=False,
    mnf=0, mnfPrint=False,
    transparent=False, ticksHide=True
):
    if transparent:
        plt.rcParams.update({
            "figure.facecolor":  (1.0, 0.0, 0.0, 0.0),
            "axes.facecolor":    (0.0, 1.0, 0.0, 0.0),
            "savefig.facecolor": (0.0, 0.0, 1.0, 0.0),
        })
    figArr = plotNodeTraces(tS, STYLE)
    axTemp = figArr[0].get_axes()[0]
    STYLE['yRange'] = (STYLE['yRange'][0], STYLE['yRange'][1] * popScaler)
    axTemp.set_xlim(STYLE['xRange'][0], STYLE['xRange'][1])
    axTemp.set_ylim(STYLE['yRange'][0], STYLE['yRange'][1])
    if autoAspect:
        axTemp.set_aspect(aspect=scaleAspect(STYLE["aspect"], STYLE))
    else:
        axTemp.set_aspect(aspect=STYLE["aspect"])
    if ticksHide:
        axTemp.axes.xaxis.set_ticklabels([])
        axTemp.axes.yaxis.set_ticklabels([])
        axTemp.axes.xaxis.set_visible(False)
        axTemp.axes.yaxis.set_visible(False)
        # axTemp.xaxis.set_tick_params(width=0)
        # axTemp.yaxis.set_tick_params(width=0)
        axTemp.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
        axTemp.set_axis_off()
    axTemp.xaxis.set_ticks(np.arange(0, STYLE['xRange'][1], 365))
    axTemp.yaxis.set_ticks(np.arange(0, STYLE['yRange'][1], STYLE['yRange'][1]/4))
    axTemp.grid(which='major', axis='y', lw=.5, ls='-', alpha=0.0, color=(0, 0, 0))
    axTemp.grid(which='major', axis='x', lw=.5, ls='-', alpha=0.0, color=(0, 0, 0))

    days = tS['landscapes'][0].shape[0]
    if (vLines[0] > 0) and (vLines[1] <= days) and (wop > 0) and (vLines[0] < vLines[1]):
        axTemp.axvspan(vLines[0], vLines[1], alpha=0.15, facecolor='#3687ff', zorder=0)
        axTemp.axvline(vLines[0], alpha=0.75, ls='-.', lw=.35, color='#3687ff', zorder=0)
        axTemp.axvline(vLines[1], alpha=0.75, ls='-.', lw=.35, color='#3687ff', zorder=0)

    if (vLines[0] > 0) and (vLines[1] <= days) and (wop > 0) and (vLines[0] > vLines[1]):
        axTemp.axvspan(vLines[0], vLines[1], alpha=0.15, facecolor='#FF5277', zorder=0)
        axTemp.axvline(vLines[0], alpha=0.75, ls='-.', lw=.35, color='#FF1A4B', zorder=0)
        axTemp.axvline(vLines[1], alpha=0.75, ls='-.', lw=.35, color='#FF1A4B', zorder=0)

    for hline in hLines:
        axTemp.axhline(hline, alpha=.25, zorder=10, ls='--', lw=.35, color='#000000')
    for vline in vLines[2:]:
        axTemp.axvline(vline, alpha=.25, zorder=10, ls='--', lw=.35, color='#000000')
    # Print metrics -----------------------------------------------------------
    if  wopPrint:
        axTemp.text(
            labelPos[0], labelPos[1], 'WOP: '+str(int(wop)),
            verticalalignment='bottom', horizontalalignment='left',
            transform=axTemp.transAxes,
            color='#00000055', fontsize=7.5
        )
    if cptPrint:
        axTemp.text(
            labelPos[0], labelPos[1]-.1, 'CPT: {:.3f}'.format(cpt),
            verticalalignment='bottom', horizontalalignment='left',
            transform=axTemp.transAxes,
            color='#00000055', fontsize=7.5
        )    
    if poePrint:
        axTemp.text(
            labelPos[0], labelPos[1]-.2, 'POE: {:.3f}'.format(poe),
            verticalalignment='bottom', horizontalalignment='left',
            transform=axTemp.transAxes,
            color='#00000055', fontsize=7.5
        )        
    if mnfPrint:
        axTemp.text(
            labelPos[0], labelPos[1]-.3, 'MIN: {:.3f}'.format(mnf),
            verticalalignment='bottom', horizontalalignment='left',
            transform=axTemp.transAxes,
            color='#00000055', fontsize=7.5
        )     
    # --------------------------------------------------------------------------
    #axTemp.tick_params(color=(0, 0, 0, 0.5))
    # extent = axTemp.get_tightbbox(figArr[0]).transformed(figArr[0].dpi_scale_trans.inverted())
    if border:
        axTemp.set_axis_on()
        plt.setp(axTemp.spines.values(), color=borderColor)
        pad = 0.025
        for axis in ['top','bottom','left','right']:
            axTemp.spines[axis].set_linewidth(borderWidth)
    else:
        pad = 0
    figArr[0].savefig(
            "{}/{}.png".format(PATH_IMG, nS),
            dpi=STYLE['dpi'], facecolor=None,
            orientation='portrait', format='png', 
            transparent=transparent, bbox_inches='tight', pad_inches=pad
        )
    plt.clf()
    plt.cla() 
    plt.close('all')
    plt.gcf()
    return None


def exportTracesPlotVideo(
    tS, nS, STYLE, PATH_IMG, 
    border=True, borderColor='#8184a7AA', borderWidth=2, autoAspect=False,
    vLines=[0, 0], popScaler=1,
    transparent=False, ticksHide=True
):
    if transparent:
        plt.rcParams.update({
            "figure.facecolor":  (1.0, 0.0, 0.0, 0.0),
            "axes.facecolor":    (0.0, 1.0, 0.0, 0.0),
            "savefig.facecolor": (0.0, 0.0, 1.0, 0.0),
        })
    figArr = plotNodeTraces(tS, STYLE)
    axTemp = figArr[0].get_axes()[0]
    axTemp.set_aspect(aspect=STYLE["aspect"])
    STYLE['yRange'] = (STYLE['yRange'][0], STYLE['yRange'][1] * popScaler)
    axTemp.set_xlim(STYLE['xRange'][0], STYLE['xRange'][1])
    axTemp.set_ylim(STYLE['yRange'][0], STYLE['yRange'][1])
    if autoAspect:
        axTemp.set_aspect(aspect=scaleAspect(STYLE["aspect"], STYLE))
    else:
        axTemp.set_aspect(aspect=STYLE["aspect"])
    if ticksHide:
        axTemp.axes.xaxis.set_ticklabels([])
        axTemp.axes.yaxis.set_ticklabels([])
        axTemp.axes.xaxis.set_visible(False)
        axTemp.axes.yaxis.set_visible(False)
        axTemp.xaxis.set_tick_params(width=2)
        axTemp.yaxis.set_tick_params(width=2)
        axTemp.set_axis_off()
    axTemp.xaxis.set_ticks(np.arange(0, STYLE['xRange'][1], 365))
    axTemp.yaxis.set_ticks(np.arange(0, STYLE['yRange'][1], STYLE['yRange'][1]/4))
    axTemp.grid(which='major', axis='y', lw=.5, ls='-', alpha=0.0, color=(0, 0, 0))
    axTemp.grid(which='major', axis='x', lw=.5, ls='-', alpha=0.0, color=(0, 0, 0))

    # for spine in axTemp.spines.values():
    #     spine.set_edgecolor('#B1C0DD77')

    days = tS['landscapes'][0].shape[0]
    axTemp.axvspan(vLines[0], vLines[1], alpha=.6, facecolor='#ffffff', zorder=5)
    axTemp.axvline(vLines[0], alpha=0.25, ls='--', lw=1, color='#B1C0DD', zorder=10)

    if border:
        axTemp.set_axis_on()
        plt.setp(axTemp.spines.values(), color=borderColor)
        pad = 0.025
        for axis in ['top','bottom','left','right']:
            axTemp.spines[axis].set_linewidth(borderWidth)
    else:
        pad = 0
    figArr[0].savefig(
            "{}/{}.png".format(PATH_IMG, nS),
            dpi=STYLE['dpi'], facecolor=None,
            orientation='portrait', format='png', 
            transparent=transparent, bbox_inches='tight', pad_inches=0
        )
    plt.clf()
    plt.cla() 
    plt.close('all')
    plt.gcf()
    return None


def getAxisRange(x):
    return (min(x), max(x))


def exportPreTracesPlotWrapper(
        expIx, fLists, STYLE, PT_IMG,
        border=True, borderColor='#322E2D', borderWidth=1, autoAspect=False,
        xpNum=0, digs=3, vLines=[0, 0], hLines=[0], popScaler=1,
        transparent=False, ticksHide=True
    ):
    ter.printProgress(expIx+1, xpNum, digs)
    (_, repDta) = [pkl.load(file) for file in (fLists[expIx])]
    name = path.splitext(fLists[expIx][0].split('/')[-1])[0][:-4]
    # Export plots --------------------------------------------------------
    exportTracesPlot(
        repDta, name, STYLE, PT_IMG, wopPrint=False, autoAspect=autoAspect,
        border=border, borderColor=borderColor, borderWidth=borderWidth,
        transparent=transparent, vLines=vLines, hLines=hLines, 
        ticksHide=ticksHide
    )
    return None


def exportPstTracesPlotWrapper(
        exIx, repFiles, xpidIx, 
        dfTTI, dfTTO, dfWOP, dfMNX, dfPOE, dfCPT,
        STABLE_T, THS, QNT, STYLE, PT_IMG, 
        border=True, borderColor='#322E2D', borderWidth=1, 
        labelPos=(.75, .95), xpsNum=0, digs=3, 
        autoAspect=False, popScaler=1,
        wopPrint=True, cptPrint=True, 
        poePrint=True, mnfPrint=True,
        transparent=False, 
        ticksHide=True
    ):
    padi = str(exIx+1).zfill(digs)
    fmtStr = '{}+ File: {}/{}'
    print(fmtStr.format(ter.CBBL, padi, len(repFiles), ter.CEND), end='\r')
    repFile = repFiles[exIx]
    (repDta, xpid) = (
            pkl.load(repFile), expHan.getXpId(repFile, xpidIx)
        )
    xpRow = [
        dataA.filterDFWithID(j, xpid, max=len(xpidIx)) for j in (
            dfTTI, dfTTO, dfWOP, dfMNX, dfPOE, dfCPT
        )
    ]
    (tti, tto, wop) = [float(row[THS]) for row in xpRow[:3]]
    (mnf, mnd, poe, cpt) = (
        float(xpRow[3]['min']), float(xpRow[3]['minx']), 
        float(xpRow[4]['POE']), float(xpRow[5]['CPT'])
    )
    # Traces ------------------------------------------------------------------
    pop = repDta['landscapes'][0][STABLE_T][-1]
    # STYLE['yRange'] = (0,  pop*popScaler)
    exportTracesPlot(
        repDta, repFile.split('/')[-1][:-6]+str(QNT), STYLE, PT_IMG,
        vLines=[tti, tto, mnd], hLines=[mnf*pop], labelPos=labelPos, 
        border=border, borderColor=borderColor, borderWidth=borderWidth,
        autoAspect=autoAspect, popScaler=popScaler,
        wop=wop, wopPrint=wopPrint, 
        cpt=cpt, cptPrint=cptPrint,
        poe=poe, poePrint=poePrint,
        mnf=mnf, mnfPrint=mnfPrint,
        transparent=transparent, ticksHide=ticksHide
    )
    return None