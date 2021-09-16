# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fledge',
 'fledge.frames',
 'fledge.generic',
 'fledge.projections',
 'fledge.references',
 'fledge.spaces',
 'fledge.transforms']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0',
 'networkx>=2.6.1,<3.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pyvis>=0.1.9,<0.2.0']

entry_points = \
{'console_scripts': ['fledge = fledge.__main__:main']}

setup_kwargs = {
    'name': 'fledge',
    'version': '0.1.0a3',
    'description': 'Fledge',
    'long_description': '|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/fledge.svg\n   :target: https://pypi.org/project/fledge/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/fledge.svg\n   :target: https://pypi.org/project/fledge/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/fledge\n   :target: https://pypi.org/project/fledge\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/fledge\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/fledge/latest.svg?label=Read%20the%20Docs\n   :target: https://fledge.readthedocs.io/\n   :alt: Read the documentation at https://fledge.readthedocs.io/\n.. |Tests| image:: https://github.com/benjamindkilleen/fledge/workflows/Tests/badge.svg\n   :target: https://github.com/benjamindkilleen/fledge/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/benjamindkilleen/fledge/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/benjamindkilleen/fledge\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\n.. image:: https://github.com/benjamindkilleen/fledge/raw/main/docs/_static/fledge_logo_text_small.png\n   :alt: Fledge logo.\n   :align: center\n\n\nDescription\n-----------\n\nFledge is an in-development project. It has a well-defined scope and initial structure but is not\nready for users. As such, the statements made here are more aspirational than actual.\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *Fledge* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install fledge\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see `Contributing`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Fledge* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nIdea and initial development by `Benjamin D. Killeen`_. Logo by `Sarah Larson`_.\nPackage layout is based on the `Hypermodern Python Cookiecutter`_ template.\nLogo font (Ainslee Sans) by `Jeremy Dooley`_.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/benjamindkilleen/fledge/issues\n.. _pip: https://pip.pypa.io/\n.. _Benjamin D. Killeen: https://benjamindkilleen.com\n.. _Sarah Larson: https://sarahmarielarson.com\n.. _Jeremy Dooley: https://fonts.adobe.com/designers/jeremy-dooley\n.. github-only\n.. _Contributing: CONTRIBUTING.rst\n.. _Usage: https://fledge.readthedocs.io/en/latest/usage.html\n',
    'author': 'Benjamin D. Killeen',
    'author_email': 'killeen@jhu.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/benjamindkilleen/fledge',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
