# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['geoh5py',
 'geoh5py.data',
 'geoh5py.groups',
 'geoh5py.io',
 'geoh5py.objects',
 'geoh5py.objects.surveys',
 'geoh5py.shared',
 'geoh5py.workspace']

package_data = \
{'': ['*']}

install_requires = \
['h5py>=3.2.1,<4.0.0', 'numpy!=1.19.4']

entry_points = \
{'console_scripts': ['publish = devtools.publish:publish']}

setup_kwargs = {
    'name': 'geoh5py',
    'version': '0.1.4',
    'description': 'Python API for geoh5, an open file format for geoscientific data',
    'long_description': 'geoh5py: Python API for geoh5. An open file format for geoscientific data\n==========================================================================\n\nThe **geoh5py** library has been created for the manipulation and storage of a wide range of\ngeoscientific data (points, curve, surface, 2D and 3D grids) in\n`geoh5 file format <https://gist.github.com/jincandescent/06a3bd4e0e54360ad191>`_.\nUsers will be able to directly leverage the powerful visualization\ncapabilities of `Geoscience ANALYST <https://mirageoscience.com/mining-industry-software/geoscience-analyst/>`_ along with open-source code from the Python ecosystem.\n\nInstallation\n^^^^^^^^^^^^\n**geoh5py** is currently written for Python 3.7 or higher, and depends on `NumPy <https://numpy.org/>`_ and\n`h5py <https://www.h5py.org/>`_.\n\n.. note:: Users will likely want to take advantage of other packages available in the Python ecosystem.\n    We therefore recommend using `Anaconda <https://www.anaconda.com/download/>`_ to manage the installation.\n\n\nInstall **geoh5py** from PyPI::\n\n    $ pip install geoh5py\n\n\nFeedback\n^^^^^^^^\nHave comments or suggestions? Submit feedback.\nAll the content can be found on the github_ repository.\n\n.. _github: https://github.com/MiraGeoscience/geoh5py\n\n\nVisit `Mira Geoscience website <https://mirageoscience.com/>`_ to learn more about our products\nand services.\n\n\nLicense\n^^^^^^^\ngeoh5py is free software: you can redistribute it and/or modify\nit under the terms of the GNU Lesser General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\n\ngeoh5py is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Lesser General Public License for more details.\n\nYou should have received a copy of the GNU Lesser General Public License\nalong with geoh5py.  If not, see <https://www.gnu.org/licenses/>.\n\n\nCopyright\n^^^^^^^^^\nCopyright (c) 2021 Mira Geoscience Ltd.\n',
    'author': 'Mira Geoscience',
    'author_email': 'support@mirageoscience.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://mirageoscience.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
