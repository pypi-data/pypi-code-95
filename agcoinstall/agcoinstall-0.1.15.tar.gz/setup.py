# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['agcoinstall']

package_data = \
{'': ['*'], 'agcoinstall': ['data/*', 'data/images/*']}

install_requires = \
['arrow>=1.1.0,<2.0.0',
 'click>=7.0,<8.0',
 'lxml>=4.6.2,<5.0.0',
 'psutil>=5.7.3,<6.0.0',
 'pyautogui>=0.9.52,<0.10.0',
 'regobj>=0.2.2,<0.3.0',
 'requests>=2.24.0,<3.0.0',
 'winapps>=0.1.6,<0.2.0']

entry_points = \
{'console_scripts': ['agcoinstall = agcoinstall.__main__:main']}

setup_kwargs = {
    'name': 'agcoinstall',
    'version': '0.1.15',
    'description': 'Agcoinstall',
    'long_description': "Agcoinstall\n===========\n\n|PyPI| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/agcoinstall.svg\n   :target: https://pypi.org/project/agcoinstall/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/agcoinstall\n   :target: https://pypi.org/project/agcoinstall\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/agcoinstall\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/agcoinstall/latest.svg?label=Read%20the%20Docs\n   :target: https://agcoinstall.readthedocs.io/\n   :alt: Read the documentation at https://agcoinstall.readthedocs.io/\n.. |Tests| image:: https://github.com/MrSuperbear/agcoinstall/workflows/Tests/badge.svg\n   :target: https://github.com/MrSuperbear/agcoinstall/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/MrSuperbear/agcoinstall/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/MrSuperbear/agcoinstall\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n\nFeatures\n--------\n\n* TODO\n\n\nRequirements\n------------\n\n* TODO\n\n\nInstallation\n------------\n\nYou can install *Agcoinstall* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install agcoinstall\n\n\nUsage\n-----\n\n* TODO\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the MIT_ license,\n*Agcoinstall* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT: http://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/MrSuperbear/agcoinstall/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n",
    'author': 'Darrin Fraser',
    'author_email': 'darrin.fraser@agcocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MrSuperbear/agcoinstall',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
