""" BioSimulators-compliant command-line interface to the
`RBApy <https://sysbioinra.github.io/RBApy/>`_ simulation program.

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-12
:Copyright: 2021, BioSimulators Team
:License: MIT
"""

from . import get_simulator_version
from ._version import __version__
from .core import exec_sedml_docs_in_combine_archive
from biosimulators_utils.simulator.cli import build_cli

__all__ = [
    'App',
    'main',
]

App = build_cli('biosimulators-rbapy', __version__,
                'RBApy', get_simulator_version(), 'https://sysbioinra.github.io/RBApy/',
                exec_sedml_docs_in_combine_archive)


def main():
    with App() as app:
        app.run()
