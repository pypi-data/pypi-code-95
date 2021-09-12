"""
Plotting functionality. All plot functions make PNG images to destination
file based on given source array(s) of data.
"""

import numpy as np
import matplotlib.pyplot as plt

plt.switch_backend("agg")


def plot_data_acquisitions(settings, dest_file, acqs, min_preds):
    """
    Plots minimum predictions and uncertainty, acquisition energies
    and locations as a function of iteration.
    """
    itNo_acqs = np.clip(acqs[:, 0], int(min_preds[0, 0]), np.inf)
    x = acqs[:, 2 : settings.dim + 2]
    y = acqs[:, settings.dim + 2]
    itNo_mp = min_preds[:, 0]
    xhat = min_preds[:, 2 : settings.dim + 2]
    muhat = min_preds[:, -2]
    nuhat = min_preds[:, -1]

    plt.subplot(211)
    plt.fill_between(itNo_mp, muhat + nuhat, muhat, color="lightgrey")
    plt.fill_between(itNo_mp, muhat - nuhat, muhat, color="lightgrey")
    plt.plot(itNo_mp, muhat + nuhat, "grey", linewidth=2)
    plt.plot(itNo_mp, muhat - nuhat, "grey", linewidth=2)
    plt.plot(itNo_mp, muhat, "black", linewidth=5, label=r"$\mu(\hat{x})$")
    plt.scatter(
        itNo_acqs,
        y,
        s=200,
        linewidth=4,
        facecolors="none",
        edgecolors="black",
        label="$acq_y$",
    )

    plt.xlim(min(itNo_mp), max(itNo_mp))
    plt.xticks(itNo_mp[:: max(1, round(len(itNo_mp) / 10))])
    plt.ylabel("$y$ with $\mu(\hat{x})$", size=20)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)

    plt.subplot(212)
    colors = [
        "blue",
        "red",
        "green",
        "brown",
        "yellow",
        "purple",
        "cyan",
        "magenta",
        "grey",
        "gold",
    ]
    for i in range(x.shape[1]):
        plt.plot(
            itNo_mp,
            xhat[:, i],
            color=colors[i % len(colors)],
            linewidth=5,
            label="$\hat{x}_%i$" % (i + 1),
        )
        plt.scatter(
            itNo_acqs,
            x[:, i],
            s=200,
            linewidth=4,
            facecolors="none",
            edgecolors=colors[i % len(colors)],
            label="$acq_{x%i}$" % (i + 1),
        )

    plt.xlim(min(itNo_mp), max(itNo_mp))
    plt.xticks(itNo_mp[:: max(1, round(len(itNo_mp) / 10))])
    plt.xlabel("iteration", size=20)
    plt.ylabel("$x_i$ with $\hat{x}_i$", size=20)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)

    plt.suptitle("Data acquisitions", size=20)
    plt.gcf().set_size_inches(9, 8)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(dest_file)
    plt.close()


def plot_conv_measures(settings, dest_file, conv_meas, legends=True):
    """
    Plots quantities related to convergence as a function of iteration.
    """
    itNo = conv_meas[:, 0]
    dxhat = conv_meas[:, 2]
    dmuhat = conv_meas[:, 3]

    plt.subplot(211)
    plt.plot(itNo, dxhat, "k", linewidth=5)
    # plt.xlabel('iteration', size=20)
    plt.ylabel(r"$\Delta \hat{x}$", size=24)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.grid(True)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)
    if max(dxhat) > 0:
        plt.yscale("log")

    plt.subplot(212)
    plt.plot(itNo, dmuhat, "k", linewidth=5)
    plt.xlabel("iteration", size=20)
    plt.ylabel(r"$abs(\Delta \mu(\hat{x}))/\Delta y$", size=24)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.grid(True)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)
    if max(dmuhat) > 0:
        plt.yscale("log")

    plt.suptitle("Convergence tracking", size=20)
    plt.gcf().set_size_inches(9, 7)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(dest_file)
    plt.close()


def plot_hyperparameters(settings, dest_file, hypers, legends=True):
    """
    Plots GP model unfixed hyperparameters (variances and lengthscales)
    as a function of iteration.
    """
    itNo = hypers[:, 0]
    var = hypers[:, 2]
    ls = hypers[:, 3:]

    colors = [
        "blue",
        "red",
        "green",
        "brown",
        "yellow",
        "purple",
        "cyan",
        "magenta",
        "black",
        "gold",
    ]
    markers = ["s", "p", "*", "h", "^", "+", "x", "d", "v", "|"]

    plt.subplot(211)
    plt.plot(itNo, var, color="r", linewidth=5)
    plt.ylabel("Variance", size=20)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.yscale("log")
    plt.grid(True)
    plt.gca().tick_params(labelsize=18)
    # plt.gca().ticklabel_format(useOffset=False)

    plt.subplot(212)
    for i in range(settings.dim):
        plt.plot(
            itNo,
            ls[:, i],
            color=colors[i % 10],
            linewidth=5,
            linestyle="-",
            marker=markers[i % 10],
            markersize=12,
            label=r"$\ell_ %i$" % (i + 1),
        )
    plt.xlabel("iteration", size=20)
    plt.ylabel("Lengthscale", size=20)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.yscale("log")
    plt.grid(True)
    plt.gca().tick_params(labelsize=18)
    # plt.gca().ticklabel_format(useOffset=False)
    if legends:
        lgd = plt.legend(loc="upper right", prop={"size": 18})

    plt.suptitle("Hyperparameter values", size=20)
    plt.gcf().set_size_inches(11, 7)
    if legends:  # FOR OLD MATPLOTLIB COMPATIBILITY
        plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
    else:
        plt.savefig(dest_file)
    plt.close()


def plot_truef_hat(settings, dest_file, truef_hats, legends=True):
    """
    Plots true function value at xhat locations
    as a function of iteration.
    """
    itNo = truef_hats[:, 0]
    truehat = truef_hats[:, -2]
    last = truehat[-1]
    best = np.array([np.min(truehat[:i]) for i in range(1, len(truehat) + 1)])
    tfhat_muhat = truef_hats[:, -1]

    plt.subplot(211)
    plt.plot(itNo, abs(truehat - last), "k", linewidth=5)
    plt.plot(itNo, abs(best - last), "k", linestyle="dashed", linewidth=3, label="best")
    plt.grid(True)
    plt.ylabel(r"$f(\hat{x})-f(\hat{x}_{last})$", size=24)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)
    if max(abs(truehat - last)) and max(abs(best - last)) > 0:
        plt.yscale("log")
    if legends:
        lgd = plt.legend(loc="upper right", prop={"size": 20})

    plt.subplot(212)
    plt.plot(itNo, abs(tfhat_muhat), "k", linewidth=5)
    plt.xlabel("iteration", size=20)
    plt.ylabel(r"$f(\hat{x})-\mu(\hat{x})$", size=24)
    plt.xticks(itNo[:: max(1, round(len(itNo) / 10))])
    plt.grid(True)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)
    if max(abs(tfhat_muhat)) > 0:
        plt.yscale("log")

    plt.suptitle("True function at minimum predictions", size=20)
    plt.gcf().set_size_inches(9, 9)
    if legends:  # FOR OLD MATPLOTLIB COMPATIBILITY
        plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
    else:
        plt.savefig(dest_file)
    plt.close()


def plot_model(
    settings,
    dest_file,
    model_data,
    xhat=None,
    acqs=None,
    xnext=None,
    minima=None,
    truef=None,
    incl_uncert=True,
    axis_labels=None,
    legends=True,
    paths=None,
):
    """
    Plots a (max 2D) slice of the model.
    """
    coords = model_data[:, : settings.dim]
    mu, nu = model_data[:, -2], model_data[:, -1]
    slice_dim = (
        1 if settings["pp_model_slice"][0] == settings["pp_model_slice"][1] else 2
    )
    if axis_labels is None:
        axis_labels = [
            "$x_%i$" % (settings["pp_model_slice"][0] + 1),
            "$x_%i$" % (settings["pp_model_slice"][1] + 1),
        ]

    if slice_dim == 1:
        x1 = coords[:, settings["pp_model_slice"][0]]
        if truef is not None:
            crds = truef[:, : settings.dim]
            tf = truef[:, -1]
            tfx1 = crds[:, settings["pp_model_slice"][0]]
            plt.plot(tfx1, tf, "k", linewidth=5, label="f(x)")
        if incl_uncert:
            plt.fill_between(x1, mu + nu, mu, color="lightgrey")
            plt.fill_between(x1, mu - nu, mu, color="lightgrey")
            plt.plot(x1, mu + nu, "grey", linewidth=3, label="$\\nu(x)$")
            plt.plot(x1, mu - nu, "grey", linewidth=3)
        plt.plot(x1, mu, "b", linewidth=5, label="$\\mu(x)$")

        if xhat is not None:
            plt.axvline(
                xhat[settings["pp_model_slice"][0]],
                color="red",
                linewidth=5,
                label="$\hat{x}$",
                zorder=19,
            )

        if acqs is not None:
            x1 = acqs[:, settings["pp_model_slice"][0]]
            y = acqs[:, -1]
            plt.scatter(
                x1,
                y,
                s=200,
                linewidth=6,
                facecolors="none",
                edgecolors="brown",
                label="acqs",
                zorder=18,
            )

        if xnext is not None:
            plt.axvline(
                xnext[settings["pp_model_slice"][0]],
                color="green",
                linewidth=5,
                label="$x_{next}$",
                linestyle="dashed",
                zorder=20,
            )

        if minima is not None:
            x1 = minima[:, settings["pp_model_slice"][0]]
            y = minima[:, -2]
            plt.scatter(
                x1,
                y,
                s=250,
                linewidth=6,
                zorder=19,
                facecolors="none",
                edgecolors="lawngreen",
                label="minima",
            )

        plt.xlim(
            min(coords[:, settings["pp_model_slice"][0]]),
            max(coords[:, settings["pp_model_slice"][0]]),
        )
        yd = max(mu) - min(mu)
        plt.ylim(min(mu) - 0.1 * yd, max(mu) + 0.1 * yd)
        plt.xlabel(axis_labels[0], size=24)
        plt.ylabel("$y$", size=24)
        if legends:
            lgd = plt.legend(
                bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                loc=3,
                ncol=4,
                mode="expand",
                borderaxespad=0.0,
                prop={"size": 20},
            )
        plt.gcf().set_size_inches(10, 8)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if legends:  # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        else:
            plt.savefig(dest_file)
        plt.close()

    elif slice_dim == 2:

        if incl_uncert:
            x1, x2, nu = _get_2d_arrays(coords, settings, nu)
            _plot_2d_contours(x1, x2, nu, label=r'$\nu(x)$')
            _plot_2d_labels_settings(axis_labels)
            plt.tight_layout()
            plt.savefig(dest_file[:-4] + "_uncert.png")
            plt.close()

        x1, x2, mu = _get_2d_arrays(coords, settings, mu)
        _plot_2d_contours(x1, x2, mu, label=r'$\mu(x)$')

        lo = False
        lo |= _plot_2d_acqs(acqs, settings)
        lo |= _plot_2d_minima(minima, settings)
        lo |= _plot_2d_xnext(xnext, settings)
        lo |= _plot_2d_xhat(xhat, settings)
        _plot_2d_paths(paths, settings)

        _plot_2d_labels_settings(axis_labels)
        if legends and lo:
            lgd = plt.legend(
                bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                loc=3,
                ncol=4,
                mode="expand",
                borderaxespad=0.0,
                prop={"size": 20},
            )
        if legends:  # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        else:
            plt.savefig(dest_file)
        plt.close()
    else:
        raise TypeError("ERROR: Model plot only applicable up to 2D (slices)")


def plot_acq_func(
    settings,
    dest_file,
    acqf_data,
    acqs=None,
    xhat=None,
    xnext=None,
    axis_labels=None,
    legends=True,
):
    """
    Plots a (max 2D) slice of the acquisition function. Can include also
    acquisitions, xhat and xnext if those are given.
    """
    coords = acqf_data[:, : settings.dim]
    af = acqf_data[:, -1]
    slice_dim = (
        1 if settings["pp_model_slice"][0] == settings["pp_model_slice"][1] else 2
    )
    if axis_labels is None:
        axis_labels = [
            "$x_%i$" % (settings["pp_model_slice"][0] + 1),
            "$x_%i$" % (settings["pp_model_slice"][1] + 1),
        ]

    if slice_dim == 1:
        x1 = coords[:, settings["pp_model_slice"][0]]
        plt.plot(x1, af, "k", linewidth=5)

        if acqs is not None:
            x1 = acqs[:, settings["pp_model_slice"][0]]
            y = acqs[:, -1]
            plt.scatter(
                x1,
                y,
                s=200,
                linewidth=6,
                facecolors="none",
                edgecolors="brown",
                label="acqs",
            )

        if xhat is not None:
            plt.axvline(
                xhat[settings["pp_model_slice"][0]],
                color="red",
                linewidth=5,
                label="$\hat{x}$",
            )

        if xnext is not None:
            plt.axvline(
                xnext[settings["pp_model_slice"][0]],
                color="green",
                linewidth=5,
                label="$x_{next}$",
                linestyle="dashed",
            )

        plt.xlim(
            min(coords[:, settings["pp_model_slice"][0]]),
            max(coords[:, settings["pp_model_slice"][0]]),
        )
        yd = max(af) - min(af)
        plt.ylim(min(af) - 0.1 * yd, max(af) + 0.1 * yd)
        plt.xlabel(axis_labels[0], size=24)
        plt.ylabel("$acqfn(x)$", size=24)
        if legends:
            lgd = plt.legend(
                bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                loc=3,
                ncol=4,
                mode="expand",
                borderaxespad=0.0,
                prop={"size": 20},
            )
        plt.gcf().set_size_inches(10, 8)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        if legends:  # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        else:
            plt.savefig(dest_file)
        plt.close()

    elif slice_dim == 2:
        x1, x2, af = _get_2d_arrays(coords, settings, af)
        _plot_2d_contours(x1, x2, af, label='$af(x)$')

        lo = False
        lo |= _plot_2d_acqs(acqs, settings)
        lo |= _plot_2d_xnext(xnext, settings)
        lo |= _plot_2d_xhat(xhat, settings)

        _plot_2d_labels_settings(axis_labels)
        if legends and lo:
            lgd = plt.legend(
                bbox_to_anchor=(0.0, 1.02, 1.0, 0.102),
                loc=3,
                ncol=4,
                mode="expand",
                borderaxespad=0.0,
                prop={"size": 20},
            )
        if legends and lo:  # FOR OLD MATPLOTLIB COMPATIBILITY
            plt.savefig(dest_file, bbox_extra_artists=(lgd,), bbox_inches="tight")
        else:
            plt.savefig(dest_file)
        plt.close()
    else:
        raise TypeError(
            "ERROR: Acquisition function plot only" + " applicable up to 2D (slices)"
        )


def plot_truef(settings, dest_file, truef_data, axis_labels=None):
    """
    Plots a (max 2D) slice of the true function.
    """
    coords = truef_data[:, : settings.dim]
    tf = truef_data[:, -1]
    slice_dim = (
        1 if settings["pp_model_slice"][0] == settings["pp_model_slice"][1] else 2
    )
    if axis_labels is None:
        axis_labels = [
            "$x_%i$" % (settings["pp_model_slice"][0] + 1),
            "$x_%i$" % (settings["pp_model_slice"][1] + 1),
        ]

    if slice_dim == 1:
        x1 = coords[:, settings["pp_model_slice"][0]]
        plt.plot(x1, tf, "k", linewidth=5)
        plt.xlim(min(x1), max(x1))
        plt.xlabel(axis_labels[0], size=24)
        plt.ylabel("$f(x)$", size=24)
        plt.title("True function", size=20)
        plt.gcf().set_size_inches(10, 8)
        plt.gca().tick_params(labelsize=18)
        plt.gca().ticklabel_format(useOffset=False)
        plt.tight_layout()
        plt.savefig(dest_file)
        plt.close()

    elif slice_dim == 2:
        x1, x2, tf = _get_2d_arrays(coords, settings, tf,
                                    npts=settings["pp_truef_npts"])
        _plot_2d_contours(x1, x2, tf, label='$f(x)$')
        _plot_2d_labels_settings(axis_labels)
        plt.title("True function", size=20)
        plt.tight_layout()
        plt.savefig(dest_file)
        plt.close()
    else:
        raise TypeError(
            "ERROR: True function plot only" + " applicable up to 2D (slices)"
        )


def _get_2d_arrays(coords, settings, data, *, npts=None):
    if npts is None:
        npts = settings["pp_model_slice"][2]
    # x1 and x2 here are like from meshgrid()
    x1 = coords[:, settings["pp_model_slice"][0]].reshape(npts, npts)
    x2 = coords[:, settings["pp_model_slice"][1]].reshape(npts, npts)
    reshaped_data = data.reshape(npts, npts)
    return x1, x2, reshaped_data


def _plot_2d_contours(x1, x2, data, *, label='data'):
    plt.contour(x1, x2, data, 25, colors='k')
    plt.pcolormesh(x1, x2, data, cmap='viridis', shading='gouraud',
                   rasterized=True)
    cbar = plt.colorbar()
    cbar.set_label(label=label, size=24)
    cbar.ax.tick_params(labelsize=18)
    plt.xlim(x1.min(), x1.max())
    plt.ylim(x2.min(), x2.max())


def _plot_2d_xhat(xhat, settings):
    if xhat is None:
        return False
    plt.plot(
        xhat[settings["pp_model_slice"][0]],
        xhat[settings["pp_model_slice"][1]],
        "r*",
        markersize=26,
        label="$\hat{x}$",
        zorder=10,
    )
    return True


def _plot_2d_acqs(acqs, settings):
    if acqs is None:
        return False
    x1 = acqs[:, settings["pp_model_slice"][0]]
    x2 = acqs[:, settings["pp_model_slice"][1]]
    sz = np.linspace(200, 500, len(x1))
    lw = np.linspace(3, 8, len(x1))
    plt.scatter(
        x1[0],
        x2[0],
        s=sz[int(len(x1) / 2.0)],
        linewidth=lw[int(len(x1) / 2.0)],
        facecolors="none",
        edgecolors="magenta",
        label="acqs",
        zorder=10,
    )
    plt.scatter(
        x1,
        x2,
        s=sz,
        linewidths=lw,
        facecolors="none",
        edgecolors="magenta",
        zorder=10,
    )
    return True


def _plot_2d_xnext(xnext, settings):
    if xnext is None:
        return False
    plt.plot(
        xnext[settings["pp_model_slice"][0]],
        xnext[settings["pp_model_slice"][1]],
        "b^",
        markersize=26,
        label="$x_{next}$",
        zorder=10,
    )
    return True


def _plot_2d_minima(minima, settings):
    if minima is None:
        return False
    x1 = minima[:, settings["pp_model_slice"][0]]
    x2 = minima[:, settings["pp_model_slice"][1]]
    plt.scatter(
        x1,
        x2,
        s=350,
        linewidth=6,
        facecolors="none",
        edgecolors="navajowhite",
        label="minima",
        zorder=10,
    )
    return True


def _plot_2d_paths(paths, settings):
    if paths is None:
        return
    threshold = min(settings["bounds"][:, 1] - settings["bounds"][:, 0]) / 2
    for path in paths:
        start = 0
        stop = 1
        while True:
            if (
                stop == path.crds.shape[0] - 1
                or np.linalg.norm(path.crds[stop, :] - path.crds[stop - 1, :])
                > threshold
            ):
                plt.plot(
                    path.crds[range(start, stop), 0],
                    path.crds[range(start, stop), 1],
                    linewidth=3.0,
                    color="red",
                )
                if stop == path.crds.shape[0] - 1:
                    break
                else:
                    start = stop
            stop += 1


def _plot_2d_labels_settings(axis_labels):
    # XXX one could use mpl.rcParams or styles to set these
    plt.xlabel(axis_labels[0], size=24)
    plt.ylabel(axis_labels[1], size=24)
    plt.gcf().set_size_inches(10, 8)
    plt.gca().tick_params(labelsize=18)
    plt.gca().ticklabel_format(useOffset=False)
