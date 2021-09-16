# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['mzn_grader']
install_requires = \
['minizinc>=0.4,<0.5', 'pyyaml>=5.4,<6.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses>=0.6,<0.7']}

entry_points = \
{'console_scripts': ['mzn-coursera = mzn_grader:coursera']}

setup_kwargs = {
    'name': 'mzn-grader',
    'version': '1.0.0',
    'description': 'A MOOC grading executable and library for MiniZinc modelling courses',
    'long_description': None,
    'author': 'Jip J. Dekker',
    'author_email': 'jip@dekker.one',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
