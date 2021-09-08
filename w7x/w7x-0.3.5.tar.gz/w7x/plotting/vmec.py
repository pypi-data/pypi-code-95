import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


def plot_fourier(fourier, **kwargs):
    """Plot fourier coefficients.

    Args:
        fourier (w7x.vmec.FourierCoefficients): fourier coefficients to plot.
        kwargs: keyword-only arguments.

    Returns:
        matplotlib.axes: axes.
    """

    if fourier.numRadialPoints == 1:
        return _plot_fourier_map(fourier, **kwargs)

    return _plot_fourier_profile(fourier, **kwargs)


def _plot_fourier_profile(fourier, **kwargs):
    """Plot fourier coefficients as radial profile.

    Args:
        fourier (w7x.vmec.FourierCoefficients): fourier coefficients to plot.
        axes (matplotlib.pyplot.axes.Axes): The axes where to plot.
        **kwargs: Options to pass to the matplotlib plotting method.

    Returns:
        The list of artist objects.
    """

    mpol = kwargs.pop('mpol', None)
    ntor = kwargs.pop('ntor', None)
    if mpol is None or ntor is None:
        raise RuntimeError("Specify at least a fourier coefficient to plot.")

    ax = kwargs.pop('axes', None)

    shape = (fourier.numRadialPoints, len(fourier.poloidalModeNumbers),
             len(fourier.toroidalModeNumbers))
    coeffs = fourier.coefficients.reshape(shape)

    radial_points = np.linspace(0, 1, fourier.numRadialPoints)

    artists = []
    for m, n in [(m, n) for m in mpol for n in ntor]:
        artists.append(ax.plot(radial_points,
                               coeffs[:, m, n + len(fourier.poloidalModeNumbers)] / np.max(
                                   np.absolute(coeffs[:, m,
                                                      n + len(fourier.poloidalModeNumbers)])),
                               label='m {} n {}'.format(m, n),
                               **kwargs))

    ax.legend()

    return artists


def _plot_fourier_map(fourier, **kwargs):
    """Plot fourier coefficients as 2D heatmap.

    Args:
        fourier (w7x.vmec.FourierCoefficients): fourier coefficients to plot.
        axes (matplotlib.pyplot.axes.Axes): The axes where to plot.

    Returns:
        The artist object.
    """

    vmin = kwargs.pop('vmin', None)
    vmax = kwargs.pop('vmax', None)
    cax = kwargs.pop('cax', None)
    orientation = kwargs.pop('orientation', 'horizontal')
    cmap = kwargs.pop('cmap', plt.get_cmap('YlGnBu_r'))
    log_norm = kwargs.pop('log', True)
    ax = kwargs.pop('axes', None)
    annotate = kwargs.pop('annotate', False)
    annotate_fmt = kwargs.pop('annotate_fmt', '{:.2f}')
    text_kw = kwargs.pop('text_kw', {})

    shape = (len(fourier.poloidalModeNumbers),
             len(fourier.toroidalModeNumbers))
    coeffs = np.reshape(fourier.coefficients, shape)

    norm = None
    if log_norm:
        coeffs = np.absolute(coeffs)
        norm = LogNorm(vmin=vmin, vmax=vmax)

    artist = ax.imshow(coeffs, origin='lower', norm=norm, cmap=cmap)

    if annotate:
        for i in range(len(fourier.poloidalModeNumbers)):
            for j in range(len(fourier.toroidalModeNumbers)):
                ax.text(j,
                        i,
                        annotate_fmt.format(coeffs[i, j]),
                        **text_kw)

    if cax is not None or orientation is not None:
        plt.colorbar(artist, cax=cax, orientation=orientation)

    ax.set_yticks(fourier.poloidalModeNumbers)
    ax.set_xticks(np.arange(0, len(fourier.toroidalModeNumbers)))
    ax.set_xticklabels(fourier.toroidalModeNumbers)
    ax.set_yticklabels(fourier.poloidalModeNumbers)
    ax.grid(False)

    return artist


def plot_surface(surface, phi, scalar=None, **kwargs):
    """Plot fourier surface.

    Args:
        surface (w7x.vmec.SurfaceCoefficients): The surface object to plot.
        phi (float): The toroidal angle to plot in rad.
        scalar (w7x.vmec.FourierCoefficients): The scalar values to plot on top.
        levels (int): The number of level curves to draw for the tricontourf method.
        cmap (string): The matplotlib colormap string value for the tricontourf method.
        axes (matplotlib.pyplot.axes.Axes): The axes where to plot.
        nRad (int): Number of radial points to plot.
        mPol (int): Number of the poloidal points to plot.
        component (string): Component of the scalar quantity to plot.
        **kwargs: Options to pass to the matplotlib plotting method.

    Returns:
        The list of artist objects.
    """

    surface_radial_points = surface.RCos.numRadialPoints

    ax = kwargs.pop("axes", None)
    levels = kwargs.pop("levels", 20)
    cmap = kwargs.pop("cmap", "RdBu_r")

    num_radial_points = kwargs.pop("nRad", 10)
    num_poloidal_points = kwargs.pop("mPol", 36)
    poloidal_grid = np.linspace(0, 2 * np.pi, num_poloidal_points)

    if surface_radial_points < num_radial_points:
        num_radial_points = surface_radial_points

    component = kwargs.pop("component", None)

    s = np.linspace(0, surface_radial_points - 1, num_radial_points, dtype=int)
    r = surface(s, poloidal_grid, phi)[0].flatten()
    z = surface(s, poloidal_grid, phi)[1].flatten()

    artists = []
    if scalar is not None:
        values = scalar(s, poloidal_grid, phi, component).flatten()
        tricnt = ax.tricontourf(r, z, values, levels=levels, cmap=cmap)
        plt.colorbar(tricnt, ax=ax)
        artists.append(tricnt)

    artists.append(ax.plot(r, z, **kwargs))
    ax.legend()

    return artists


def _plot_vmec_coil_currents(data, **kwargs):
    """Generate axis for coil currents plot.

    Args:
        data (pandas.DataFrame): Data to plot.
        **kwargs: Options to pass to matplotlib plotting method.

    Returns:
        list: List of matplotlib.axes.Axes.
    """

    _cols = 3
    _rows = 3

    currents = ["i1", "i2", "i3", "i4", "i5", "iA", "iB"]

    # @amerlo: Because pandas is used only here I do not (yet) want to depend on
    # it. I want to keep w7x slim for deployment. Thus I put the import here.
    import pandas as pd

    df = pd.DataFrame(data.values.tolist(), columns=currents, index=data.index)

    _, axs = plt.subplots(_rows, _cols, constrained_layout=True, **kwargs)

    artists = []
    for ax, current in zip(axs.flat, currents):
        ax.set_title(current)
        artists.append(df[current].plot(kind="hist", ax=ax))

    return artists


def _plot_vmec_profile(data, **kwargs):
    """Plot vmec profile.

    Args:
        data (pandas.DataFrame): Data to plot.
        axes (matplotlib.pyplot.axes.Axes): The axes where to plot.
        **kwargs: Options to pass to matplotlib plotting method.

    Returns:
        List of artist objects.
    """

    axes = kwargs.pop("axes", plt.gca())
    s = np.linspace(0.0, 1.0, len(data.iloc[0]))

    artists = []
    for _, profile in data.items():
        artists.append(axes.plot(s, profile))

    return artists


def plot_vmec(data, feature, **kwargs):
    """Plot vmec runs data.

    Args:
        data (pandas.DataFrame): Data to plot.
        feature (string): data column to plot.
        **kwargs: Options to pass to the matplotlib plotting method.

    Returns:
        Artist or list of artist objects.
    """

    _profiles = ["pressure", "iota", "toroidalCurrent"]

    if feature == "coilCurrents":
        return _plot_vmec_coil_currents(data[feature], **kwargs)
    elif feature in _profiles:
        return _plot_vmec_profile(data[feature], **kwargs)
    else:
        return data[feature].plot(kind="hist", **kwargs)
