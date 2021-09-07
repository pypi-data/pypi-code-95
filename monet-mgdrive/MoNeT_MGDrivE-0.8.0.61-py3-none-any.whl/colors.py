
import matplotlib
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap



def addHexOpacity(colors, alpha='1A'):
    return [c+alpha for c in colors]


def replaceHexOpacity(colors, alpha='FF'):
    return [i[:-2]+alpha for i in colors]



def generateAlphaColorMapFromColor(
    color
):
    """
    Description:
        * Generates the cmap necessary to do the landscape heatmaps.
    In:
        * color: hex color to alpha cmap
    Out:
        * cmap: Color map changing in alpha
    Notes:
        * NA
    """
    alphaMap = LinearSegmentedColormap.from_list(
        'tempMap',
        [(0.0, 0.0, 0.0, 0.0), color],
        gamma=0
    )
    return alphaMap


def generateAlphaColorMapFromColorArray(
    colorArray
):
    """
    Description:
        * Generates a list of cmaps from a colors list.
    In:
        * colorArray: Array containing the colors to cmap.
    Out:
        * cmapsList: List of cmaps
    Notes:
        * NA
    """
    elementsNumb = len(colorArray)
    cmapsList = [None] * elementsNumb
    for i in range(0, elementsNumb):
        cmapsList[i] = generateAlphaColorMapFromColor(colorArray[i])
    return cmapsList


def colorPaletteFromHexList(clist):
    c = mcolors.ColorConverter().to_rgb
    clrs = [c(i) for i in clist]
    rvb = mcolors.LinearSegmentedColormap.from_list("", clrs)
    return rvb

###############################################################################
# Colors
#   Ecology, Health, Trash, Wild
###############################################################################
COLEN = ['#2614ed', '#FF006E', '#45d40c', '#8338EC', '#1888e3', '#BC1097', '#FFE93E', '#3b479d']
COLHN = ['#FF006E', '#8338EC', '#0C4887']
COLTN = ['#00a2fe', '#8338EC', '#0C4887']
COLWN = ['#0eeb10', '#8338EC', '#0C4887']
# Auto-generate colorsets with required alphas --------------------------------
(COLEN, COLHN, COLTN, COLWN) = [addHexOpacity(i, alpha='1A') for i in (COLEN, COLHN, COLTN, COLWN)]
(COLEO, COLHO, COLTO, COLWO) = [replaceHexOpacity(i, alpha='FF') for i in (COLEN, COLHN, COLTN, COLWN)]
(COLEM, COLHM, COLTM, COLWM) = [generateAlphaColorMapFromColorArray(COLWO) for i in (COLEO, COLHO, COLTO, COLWO)]


[i/255 for i in (131, 56, 236)]

# #############################################################################
# Color Palette for Heatmaps
# #############################################################################
cdict = {
        'red':  ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (0.5, 0.25, 0.25), (1.0, 0.0, 0.0)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (0.5, 0.3, 0.3), (1.0, 0.0, 0.0)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (0.5, 1.0, 1.0), (1.0, 0.25, 0.25))
    }
cmapB = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)
cdict = {
        'red':      ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.95, 0.95)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0, 0)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.4, 0.4))
    }
cmapC = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)
cdict = {
        'red':      ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0, 0)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.65, 0.65)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, .95, .95))
    }
cmapM = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)
cdict = {
        'red':      ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.05, 0.05)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.91, 0.91)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.06, 0.06))
    }
cmapW = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)
cdict = {
        'red':      ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.5, 0.5)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.2, 0.2)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.9, 0.9))
    }
cmapP = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)
cdict = {
        'red':      ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.5, 0.5)),
        'green':    ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.2, 0.2)),
        'blue':     ((0.0, 1.0, 1.0), (0.1, 1.0, 1.0), (1.0, 0.9, 0.9))
    }
cmapP = matplotlib.colors.LinearSegmentedColormap('cmapK', cdict, 256)



# Define 5 colormaps ranging from transparent to opaque.
cdict1 = {
    'red':   ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    'green': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'blue':  ((0.0, 0.0, 0.0), (1.0, 0.3, 0.3)),
    'alpha': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
}
red1 = LinearSegmentedColormap('Red1', cdict1)

cdict2 = {
    'red':   ((0.0, 0.3, 0.3), (1.0, 0.3, 0.3)),
    'green': ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5)),
    'blue':  ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    'alpha': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
}
light_blue1 = LinearSegmentedColormap('LightBlue1', cdict2)

cdict3 = {
    'red':   ((0.0, 0.5, 0.5), (1.0, 0.5, 0.5)),
    'green': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'blue':  ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    'alpha': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
}
purple1 = LinearSegmentedColormap('Purple1', cdict3)

cdict4 = {
    'red':   ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    'green': ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'blue':  ((0.0, 1.0, 1.0), (1.0, 1.0, 1.0)),
    'alpha': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
}
pink1 = LinearSegmentedColormap('Pink1', cdict4)

cdict5 = {
    'red':   ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
    'green': ((0.0, 0.25, 0.25), (1.0, 0.25, 0.25)),
    'blue':  ((0.0, 0.75, 0.75), (1.0, 0.75, 0.75)),
    'alpha': ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
}
dark_blue1 = LinearSegmentedColormap('DarkBlue1', cdict5)

rgba_colors = [
    (1, 0, 0.3, 0.7), (1, 0, 1, 0.7),
    (0.5, 0, 1, 0.7), (0, 0.325, 0.75, 0.7)
]
cmaps = [light_blue1, red1, purple1, pink1, dark_blue1]



# #############################################################################
# Color Palettes for trace curves
# #############################################################################
clistPurple = [
    '#000000', '#03045e', '#6247aa', '#815ac0', '#c19ee0', '#d6e3f8'
]
CL_PURPLE = colorPaletteFromHexList(clistPurple)
clistRWB = [
    '#fe1d23', '#fe576f', '#fdcbff', '#d6e3f8', 
    '#aacbff', '#00affe', '#013af4', '#0000ee'
]
CL_RWB = colorPaletteFromHexList(clistRWB)