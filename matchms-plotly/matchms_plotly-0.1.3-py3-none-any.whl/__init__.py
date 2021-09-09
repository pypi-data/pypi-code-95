import pkg_resources
from .plot import plot_spectrum, plot_spectra

__version__ = pkg_resources.get_distribution("matchms_plotly").version
__all__ = ["plot_spectrum", "plot_spectra"]
