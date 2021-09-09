# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['skimpy']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'pandas>=1.3.2,<2.0.0',
 'rich>=10.9.0,<11.0.0',
 'typeguard>=2.12.1,<3.0.0']

entry_points = \
{'console_scripts': ['skimpy = skimpy.__main__:main']}

setup_kwargs = {
    'name': 'skimpy',
    'version': '0.0.3',
    'description': 'skimpy',
    'long_description': 'skimpy\n======\n\n|PyPI| |Status| |Python Version| |License|\n\n|Read the Docs| |Tests| |Codecov| |Downloads|\n\n|pre-commit| |Black| |Google Colab|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/skimpy.svg\n   :target: https://pypi.org/project/skimpy/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/skimpy.svg\n   :target: https://pypi.org/project/skimpy/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/skimpy\n   :target: https://pypi.org/project/skimpy\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/pypi/l/skimpy\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/skimpy/latest.svg?label=Read%20the%20Docs\n   :target: https://skimpy.readthedocs.io/\n   :alt: Read the documentation at https://skimpy.readthedocs.io/\n.. |Tests| image:: https://github.com/aeturrell/skimpy/workflows/Tests/badge.svg\n   :target: https://github.com/aeturrell/skimpy/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/aeturrell/skimpy/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/aeturrell/skimpy\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n.. |Google Colab| image:: https://colab.research.google.com/assets/colab-badge.svg\n   :target: https://colab.research.google.com/gist/aeturrell/7bf183c559dc1d15ab7e7aaac39ea0ed/skimpy_demo.ipynb\n   :alt: Google Colab\n.. |Downloads| image:: https://static.pepy.tech/badge/skimpy\n   :target: https://pepy.tech/project/skimpy\n   :alt: Downloads\n\n\nWelcome\n-------\n\nWelcome to *skimpy*! *skimpy* is a light weight tool that provides summary statistics about variables in data frames within the console. Think of it as a super version of `df.summary()`.\n\nQuickstart\n----------\n\n*skim* a dataframe and produce summary statistics within the console using:\n\n.. code:: python\n\n   from skimpy import skim\n\n   skim(df)\n\nIf you need to a dataset to try *skimpy* out on, you can use the built-in test dataframe:\n\n.. code:: python\n\n   from skimpy import skim, generate_test_data\n\n   df = generate_test_data()\n   skim(df)\n\n.. image:: https://raw.githubusercontent.com/aeturrell/skimpy/master/img/skimpy_example.png\n   :width: 600\n\nIt is recommended that you set your datatypes before using *skimpy* (for example converting any text columns to pandas string datatype), as this will produce richer statistical summaries.\n\n*skim* accepts keyword arguments that change the colour of the datatypes as displayed. For example, to change the colour of datetimes to be chartreuse instead of red, the code is:\n\n.. code:: python\n\n   skim(df, datetime="chartreuse1")\n\nYou can also change the colours of the headers of the first three summary tables using, for example,\n\n.. code:: python\n\n   skim(df, header_style="italic green")\n\nYou can try this package out right now in your browser using this `Google Colab notebook`_ (requires a Google account). Note that the Google Colab notebook uses the latest package released on PyPI (rather than the development release).\n\nFeatures\n--------\n\n* Support for boolean, numeric, datetime, string, and category datatypes\n* Command line interface in addition to interactive console functionality\n* Light weight, with results printed to terminal using the `rich`_ package.\n* Support for different colours for different types of output\n\nRequirements\n------------\n\nYou can find a full list of requirements in the pyproject.toml file. The main requirements are:\n\n* python = ">=3.7.1,<4.0.0"\n* click = "^8.0.1"\n* rich = "^10.9.0"\n* pandas = "^1.3.2"\n\n\nInstallation\n------------\n\nYou can install the latest release of *skimpy* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install skimpy\n\nTo install the development version from git, use:\n\n.. code:: console\n\n   $ pip install git+https://github.com/aeturrell/skimpy.git\n\nFor development, see the `Contributor Guide`_.\n\nUsage\n-----\n\nThis package is mostly designed to be used within an interactive console session or Jupyter notebook\n\n.. code-block:: python\n\n   from skimpy import skim\n\n   skim(df)\n\nHowever, you can also use it on the command line:\n\n.. code:: console\n\n   $ skimpy file.csv\n\n*skimpy* will do its best to infer column datatypes.\n\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*skimpy* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_\'s `Hypermodern Python Cookiecutter`_ template.\n\nskimpy was inspired by the R package `skimr`_ and by exploratory Python packages including `pandas_profiling`_ and `dataprep`_.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/aeturrell/skimpy/issues\n.. _pip: https://pip.pypa.io/\n.. _skimr: https://docs.ropensci.org/skimr/articles/skimr.html\n.. _pandas_profiling: https://pandas-profiling.github.io/pandas-profiling\n.. _dataprep: https://dataprep.ai/\n.. _rich: https://github.com/willmcgugan/rich\n.. _Google Colab notebook: https://colab.research.google.com/gist/aeturrell/7bf183c559dc1d15ab7e7aaac39ea0ed/skimpy_demo.ipynb\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n',
    'author': 'Arthur Turrell',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aeturrell/skimpy',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
