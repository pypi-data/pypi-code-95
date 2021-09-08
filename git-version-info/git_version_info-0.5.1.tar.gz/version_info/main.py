""" version_info.py

This module defines a function, `version_info`, which returns a string
describing the current git version of the highest project in the calling tree.
"""
import importlib
import subprocess

try:
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes

    matplotlib_present = True
except ImportError:
    matplotlib_present = False


command = "git describe --tags --long --dirty --always"
untracked_cmd = "git status --porcelain"
fmt = "{tag}_{commitcount}+{gitsha}{dirty}"


def get_version() -> str:
    """
    Returns a string describing the git version of the given project.

    :param ax: Axes object for the chart whose name will be updated. Unused if alter_plot is false, set to
    `matplotlib.pyplot.gca()` by default
    :return: A string describing the project's version
    """

    try:
        version = subprocess.check_output(command, universal_newlines=True).strip()

        # Thanks to pyfidelity/setuptools-git-version
        try:
            parts = version.split("-")
            assert len(parts) in (3, 4)
            dirty = len(parts) == 4
            tag, count, sha = parts[:3]
            if count == "0" and not dirty:
                return tag

            # Check for untracked files too
            if not dirty:
                if subprocess.check_output(
                    untracked_cmd, universal_newlines=True
                ).strip():
                    dirty = True

            if dirty:
                dirty_str = "-D"
            else:
                dirty_str = ""

            return fmt.format(
                tag=tag, commitcount=count, gitsha=sha.lstrip("g"), dirty=dirty_str
            )
        except AssertionError:
            return version
    except FileNotFoundError:
        # Git is not installed
        return "unknown-version"


def tag_plot(ax=None, small=False, tag_text=None) -> str:
    """
    Tags the passed Axes object with the project's current version.

    Parameters
    ----------
    ax : Axes, optional
        Axes object for the chart whose name will be updated. Defaults to
        `matplotlib.pyplot.gca()`
    small : bool, optional
        If True, don't append to title but plot in corner instead. The default is False.
    tag_text : str, optional
        If passed, don't ask git for the version and just plot this text instead.

    Returns
    -------
    str
        A string describing the project's version

    """

    if not matplotlib_present:
        raise ImportError("Could not import matplotlib")

    if tag_text is None:
        ver = get_version()
    else:
        ver = tag_text

    if not ax:
        ax = plt.gca()

    if small:
        ax.figure.text(
            0.9,
            0.9,
            ver,
            fontsize=6,
            horizontalalignment="right",
        )
    else:
        current_title = ax.get_title()
        new_title = "%s\nVersion #%s" % (current_title, ver)
        ax.set_title(new_title)

    return ver


if __name__ == "__main__":
    print('Current version is "{}"'.format(get_version()))
