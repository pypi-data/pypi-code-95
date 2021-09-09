# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pocketutils',
 'pocketutils.biochem',
 'pocketutils.core',
 'pocketutils.logging',
 'pocketutils.misc',
 'pocketutils.notebooks',
 'pocketutils.plotting',
 'pocketutils.tools']

package_data = \
{'': ['*']}

install_requires = \
['orjson>=3.4,<4.0', 'regex>=2021', 'tomlkit>=0.7,<1.0']

extras_require = \
{'all': ['defusedxml>=0.7,<1.0',
         'dill>=0.3,<1.0',
         'jsonpickle>=2.0,<3.0',
         'joblib>=1.0,<2.0',
         'numpy>=1.19,<2.0',
         'pandas>=1.2,<2.0',
         'matplotlib>=3.3,<4.0',
         'goatools>=1.0,<2.0',
         'requests>=2.0,<3.0',
         'uniprot>=1.3,<2.0',
         'colorama>=0.4,<1.0',
         'psutil>=5.0,<6.0',
         'ipython>=7.0,<8.0'],
 'biochem': ['numpy>=1.19,<2.0',
             'pandas>=1.2,<2.0',
             'goatools>=1.0,<2.0',
             'requests>=2.0,<3.0',
             'uniprot>=1.3,<2.0'],
 'misc': ['colorama>=0.4,<1.0', 'psutil>=5.0,<6.0'],
 'notebooks': ['pandas>=1.2,<2.0', 'ipython>=7.0,<8.0'],
 'plotting': ['numpy>=1.19,<2.0', 'pandas>=1.2,<2.0', 'matplotlib>=3.3,<4.0'],
 'tools': ['defusedxml>=0.7,<1.0',
           'dill>=0.3,<1.0',
           'jsonpickle>=2.0,<3.0',
           'joblib>=1.0,<2.0',
           'numpy>=1.19,<2.0',
           'pandas>=1.2,<2.0']}

setup_kwargs = {
    'name': 'pocketutils',
    'version': '0.5.2',
    'description': 'Adorable little Python code for you to copy or import.',
    'long_description': '# pocketutils\n\n[![Version status](https://img.shields.io/pypi/status/pocketutils?label=status)](https://pypi.org/project/pocketutils)\n[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)\n[![Python version compatibility](https://img.shields.io/pypi/pyversions/pocketutils?label=Python)](https://pypi.org/project/pocketutils)\n[![Version on Docker Hub](https://img.shields.io/docker/v/dmyersturnbull/pocketutils?color=green&label=Docker%20Hub)](https://hub.docker.com/repository/docker/dmyersturnbull/pocketutils)\n[![Version on Github](https://img.shields.io/github/v/release/dmyersturnbull/pocketutils?include_prereleases&label=GitHub)](https://github.com/dmyersturnbull/pocketutils/releases)\n[![Version on PyPi](https://img.shields.io/pypi/v/pocketutils?label=PyPi)](https://pypi.org/project/pocketutils)  \n[![Build (Actions)](https://img.shields.io/github/workflow/status/dmyersturnbull/pocketutils/Build%20&%20test?label=Tests)](https://github.com/dmyersturnbull/pocketutils/actions)\n[![Documentation status](https://readthedocs.org/projects/pocketutils/badge)](https://pocketutils.readthedocs.io/en/stable/)\n[![Coverage (coveralls)](https://coveralls.io/repos/github/dmyersturnbull/pocketutils/badge.svg?branch=main&service=github)](https://coveralls.io/github/dmyersturnbull/pocketutils?branch=main)\n[![Maintainability (Code Climate)](https://api.codeclimate.com/v1/badges/eea2b741dbbbb74ad18a/maintainability)](https://codeclimate.com/github/dmyersturnbull/pocketutils/maintainability)\n[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/dmyersturnbull/pocketutils/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/dmyersturnbull/pocketutils/?branch=main)\n\nAdorable little Python functions for you to copy or import.\n\n`pip install pocketutils`. To get the optional packages, use:\n`pip install pocketutils[tools,biochem,misc,notebooks,plotting]`\n\n\n[Apache](https://spdx.org/licenses/Apache-2.0.html)-licensed. To\n\n\nAmong the more useful are `zip_strict`, `frozenlist`, `SmartEnum`, `is_lambda`, `strip_paired_brackets`,\n`sanitize_path_node`, `TomlData`, `NestedDocDict`, `PrettyRecordFactory`, `parallel_with_cursor`,\n`loop_timing`, `HashableFile`, `QueryExecutor`, `WebResource`, `get_env_info`, `git_description`, `git_hash`,\n`delete_surefire`, `roman_to_arabic`, `pretty_float`, `pretty_function`, `round_to_sigfigs`,\n`prompt_yes_no`, and `stream_cmd_call`.\n\nAlso has functions for plotting, machine learning, and bioinformatics.\nSome of the more useful are `ConfusionMatrix`, `DecisionFrame`,\n[`PeakFinder`](https://en.wikipedia.org/wiki/Topographic_prominence), `AtcParser` (for PubChem ATC codes),\n`WellBase1` (for multiwell plates), and [`TissueTable`](https://www.proteinatlas.org/).\n\n[See the docs 📚](https://pocketutils.readthedocs.io/en/stable/), or just\n[browse the code](https://github.com/dmyersturnbull/pocketutils/tree/main/pocketutils).\n\n[New issues](https://github.com/dmyersturnbull/pocketutils/issues) and pull requests are welcome.\nPlease refer to the [contributing guide](https://github.com/dmyersturnbull/pocketutils/blob/main/CONTRIBUTING.md)\nand [security policy](https://github.com/dmyersturnbull/pocketutils/blob/main/SECURITY.md).  \nGenerated with tyrannosaurus: `tyrannosaurus new tyrannosaurus`\n',
    'author': 'Douglas Myers-Turnbull',
    'author_email': None,
    'maintainer': 'Douglas Myers-Turnbull',
    'maintainer_email': None,
    'url': 'https://github.com/dmyersturnbull/pocketutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
