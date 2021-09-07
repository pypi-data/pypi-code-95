

def removeTicksAndLabels(ax):
    """Deletes all the ticks and labels from the plot axes passed as argument.

    Parameters
    ----------
    ax: Matplotlib axes.
        Can be obtained from a figure with: fig.get_axes()[0]

    Returns
    -------
    ax
        Returns the changed ax with the modification performed.

    """
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xticks([])
    ax.set_yticks([])
    return ax


def setRange(ax, style):
    """Re-scales the plot to the range stated on the 'style' element.

    Parameters
    ----------
    ax : Matplotlib axes
        Can be obtained from a figure with: fig.get_axes()[0]
    style : Plot-style dictionary.
        Should contain:
            style['xRange'] = (lo, hi)
            style['yRange'] = (lo, hi)

    Returns
    -------
    ax
        Returns the changed ax with the modification performed.

    """
    ax.set_xlim(style['xRange'][0], style['xRange'][1])
    ax.set_ylim(style['yRange'][0], style['yRange'][1])
    return ax


def printVLines(
            ax, xCoords,
            width=.05, color='gray', alpha=.75, lStyle='--'
        ):
    """Adds vertical lines to the plot in the list of x-coordinates passed.
        Created as an auxiliary function to mark days at which events happen
        (threshold crossings).

    Parameters
    ----------
    ax : Matplotlib axes
        Can be obtained from a figure with: fig.get_axes()[0]
    xCoords : list
        A list containing the xCoordinates of all the lines to print.
    width : float
        Line width (weight).
    color : color
        Color id for the lines to be drawn.
    alpha : float
        Alpha to apply to the lines.
    lStyle : Matplotlib line-style
        Matplotlib dash-line style:
        https://matplotlib.org/gallery/lines_bars_and_markers/line_styles_reference.html

    Returns
    -------
    ax
        Returns the changed ax with the modification performed.

    """
    for vLine in xCoords:
        ax.axvline(
                x=vLine, linewidth=width, linestyle=lStyle,
                color=color, alpha=alpha
            )
    return ax


def printMinLines(
            ax, minTuple, style,
            width=.05, color='red', alpha=.75, lStyle='--'
        ):
    """Adds the lines that point towards a specific xy point. Coded to show the
        time at which the population reaches its minimum according to a given
        metric.

    Parameters
    ----------
    ax : Matplotlib axes
        Can be obtained from a figure with: fig.get_axes()[0]
    minTuple : tuple
        (x, y) coordinates tuple of the population min.
    style : Plot-style dictionary.
        Should contain:
            style['xRange'] = (lo, hi)
            style['yRange'] = (lo, hi)
    width : float
        Line width (weight).
    color : color
        Color id for the lines to be drawn.
    alpha : float
        Alpha to apply to the lines.
    lStyle : Matplotlib line-style
        Matplotlib dash-line style:
        https://matplotlib.org/gallery/lines_bars_and_markers/line_styles_reference.html

    Returns
    -------
    ax
        Returns the changed ax with the modification performed.
    """
    ax.axhline(
            y=minTuple[1], xmin=0, xmax=minTuple[0]/style['xRange'][1],
            linewidth=width, linestyle=lStyle, color=color, alpha=alpha
        )
    ax.axvline(
            x=minTuple[0], ymin=0, ymax=minTuple[1]/style['yRange'][1],
            linewidth=width, linestyle=lStyle, color=color, alpha=alpha
        )
    return ax
