# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nbpreview',
 'nbpreview.component',
 'nbpreview.component.content',
 'nbpreview.component.content.output',
 'nbpreview.component.content.output.result',
 'nbpreview.data']

package_data = \
{'': ['*'], 'nbpreview': ['templates/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'Pillow>=8.3.1,<9.0.0',
 'Pygments>=2.10.0,<3.0.0',
 'html2text>=2020.1.16,<2021.0.0',
 'httpx>=0.19.0,<0.20.0',
 'ipython>=7.27.0,<8.0.0',
 'lxml>=4.6.3,<5.0.0',
 'nbformat>=5.1.2,<6.0.0',
 'picharsso>=2.0.1,<3.0.0',
 'pylatexenc>=2.10,<3.0',
 'rich>=10.9.0,<11.0.0',
 'terminedia>=0.4.1,<0.5.0',
 'typer>=0.4.0,<0.5.0',
 'types-click>=7.1.5,<8.0.0']

entry_points = \
{'console_scripts': ['nbp = nbpreview.__main__:app',
                     'nbpreview = nbpreview.__main__:app']}

setup_kwargs = {
    'name': 'nbpreview',
    'version': '0.2.0',
    'description': 'nbpreview',
    'long_description': "nbpreview\n=========\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov|\n\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/nbpreview.svg\n   :target: https://pypi.org/project/nbpreview/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/nbpreview.svg\n   :target: https://pypi.org/project/nbpreview/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/nbpreview\n   :target: https://pypi.org/project/nbpreview\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/nbpreview\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/nbpreview/latest.svg?label=Read%20the%20Docs\n   :target: https://nbpreview.readthedocs.io/\n   :alt: Read the documentation at https://nbpreview.readthedocs.io/\n.. |Tests| image:: https://github.com/paw-lu/nbpreview/workflows/Tests/badge.svg\n   :target: https://github.com/paw-lu/nbpreview/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/paw-lu/nbpreview/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/paw-lu/nbpreview\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nA terminal viewer for Jupyter notebooks.\n\nFeatures\n--------\n\n* Render accurate(ish) Jupyter notebooks in your terminal.\n  Like cat (or bat) for ipynb files.\n\n\nRequirements\n------------\n\n* Python 3.8+\n\n\nInstallation\n------------\n\nYou can install *nbpreview* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install nbpreview\n\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*nbpreview* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/paw-lu/nbpreview/issues\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://nbpreview.readthedocs.io/en/latest/usage.html\n",
    'author': 'Paulo S. Costa',
    'author_email': 'Paulo.S.Costa5@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/paw-lu/nbpreview',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
