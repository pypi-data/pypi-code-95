# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_hplc']

package_data = \
{'': ['*']}

install_requires = \
['pyserial>=3.5,<4.0']

setup_kwargs = {
    'name': 'py-hplc',
    'version': '1.0.3',
    'description': 'An unoffical Python wrapper for the SSI-Teledyne Next Generation class HPLC pumps.',
    'long_description': '=================================================================================================\npy-hplc |license| |python| |pypi| |build-status| |docs| |style| |code quality| |maintainability|\n=================================================================================================\n\nOverview\n==========\nAn unoffical Python wrapper for the SSI-Teledyne Next Generation class HPLC pumps.\n\n- `Download page`_\n- `API Documentation`_\n- `Official pump documentation`_\n\n\nIf you notice something weird, fragile, or otherwise encounter a bug, please open an `issue`_.\n\nInstallation\n=============\nThe package is available on PyPI.\n\n``python -m pip install --user py-hplc``\n\n\nUsing the package\n==================\n\n.. image:: https://raw.githubusercontent.com/pct-code/py-hplc/main/docs/demo.gif\n  :alt: gif demonstrating example usage\n\nYou can open a pump instance like this ::\n\n  >>> from py_hplc import NextGenPump\n  >>> pump = NextGenPump("COM3")  # or "/dev/ttyUSB0", etc.\n\nOr like this ::\n\n  >>> from py_hplc import NextGenPump\n  >>> from serial import Serial\n  >>> device = Serial("COM3")  # or "/dev/ttyUSB0", etc.\n  >>> pump = NextGenPump(device)\n\nYou can inspect the pump for useful information such as its pressure units, firmware version, max flowrate, etc. ::\n\n  >>> pump.version\n  \'191017 Version 2.0.8\'\n  >>> pump.pressure_units\n  \'psi\'\n  >>> pump.pressure\n  100\n\nThe interface behaves in a typical way. Pumps can be inspected or configured without the use of getters and setters. ::\n\n  >>> pump.flowrate\n  10.0\n  >>> pump.flowrate = 5.5  # mL / min\n  >>> pump.flowrate\n  5.5\n  >>> pump.run()\n  \'OK/\'\n  >>> pump.is_running\n  True\n  >>> pump.stop()\n  \'OK/\'\n  >>> pump.is_running\n  False\n  >>> pump.leak_detected\n  False\n\n| Some pump commands, such as "CC" (current conditions), return many pieces of data at once.\n| This package makes the data available in concise, descriptive, value-typed dataclasses.\n\n::\n\n  >>> pump.current_conditions()\n  CurrentConditions(pressure=0, flowrate=10.0, response=\'OK,0000,10.00/\')\n  >>> pump.read_faults()\n  Faults(motor_stall_fault=False, upper_pressure_fault=False, lower_pressure_fault=False, response=\'OK,0,0,0/\')\n\nSee the `API Documentation`_ for more usage examples.\n\nLicense / Author\n================\nReleased under the MIT license, (C) 2021.\n\nWritten by `@teauxfu`_ for `Premier Chemical Technologies, LLC`_ .\n\n.. _`Download page`: https://pypi.org/project/py-hplc/\n\n.. _`API Documentation`: https://py-hplc.readthedocs.io/en/latest/\n\n.. _`Official pump documentation`: https://www.teledynessi.com/Manuals%20%20Guides/Product%20Guides%20and%20Resources/Serial%20Pump%20Control%20for%20Next%20Generation%20SSI%20Pumps.pdf\n\n.. _`issue`: https://github.com/pct-code/py-hplc/issues\n\n.. _`@teauxfu`: https://github.com/teauxfu\n\n.. _`Premier Chemical Technologies, LLC`: https://premierchemical.tech\n\n.. |license| image:: https://img.shields.io/github/license/pct-code/py-hplc\n  :target: https://github.com/pct-code/py-hplc/blob/main/LICENSE.txt\n  :alt: GitHub\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/py-hplc\n  :alt: PyPI - Python Version\n\n.. |pypi| image:: https://img.shields.io/pypi/v/py-hplc\n  :target: https://pypi.org/project/py-hplc/\n  :alt: PyPI\n\n.. |build-status| image:: https://github.com/pct-code/py-hplc/actions/workflows/build.yml/badge.svg\n  :target: https://github.com/pct-code/py-hplc/actions/workflows/build.yml\n  :alt: Build Status\n\n.. |docs| image:: https://readthedocs.org/projects/pip/badge/?version=stable\n  :target: https://py-hplc.readthedocs.io/en/latest/\n  :alt: Documentation Status\n\n.. |style| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n  :target: https://github.com/psf/black\n  :alt: Style\n\n.. |code quality| image:: https://img.shields.io/badge/code%20quality-flake8-black\n  :target: https://gitlab.com/pycqa/flake8\n  :alt: Code quality\n  \n.. |maintainability| image:: https://api.codeclimate.com/v1/badges/dde06c3f3ca89a3bbfb1/maintainability\n   :target: https://codeclimate.com/github/pct-code/py-hplc/maintainability\n   :alt: Maintainability\n\n',
    'author': 'Alex W',
    'author_email': 'alex@southsun.tech',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pct-code/py-hplc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
