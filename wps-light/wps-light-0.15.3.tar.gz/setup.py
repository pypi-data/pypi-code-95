# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wemake_python_styleguide',
 'wemake_python_styleguide.compat',
 'wemake_python_styleguide.logic',
 'wemake_python_styleguide.logic.arguments',
 'wemake_python_styleguide.logic.complexity',
 'wemake_python_styleguide.logic.naming',
 'wemake_python_styleguide.logic.scopes',
 'wemake_python_styleguide.logic.tokens',
 'wemake_python_styleguide.logic.tree',
 'wemake_python_styleguide.options',
 'wemake_python_styleguide.presets',
 'wemake_python_styleguide.presets.topics',
 'wemake_python_styleguide.presets.types',
 'wemake_python_styleguide.transformations',
 'wemake_python_styleguide.transformations.ast',
 'wemake_python_styleguide.vendor',
 'wemake_python_styleguide.violations',
 'wemake_python_styleguide.visitors',
 'wemake_python_styleguide.visitors.ast',
 'wemake_python_styleguide.visitors.ast.complexity',
 'wemake_python_styleguide.visitors.ast.naming',
 'wemake_python_styleguide.visitors.filenames',
 'wemake_python_styleguide.visitors.tokenize']

package_data = \
{'': ['*']}

install_requires = \
['astor>=0.8,<0.9',
 'attrs',
 'flake8-polyfill>=1.0.2,<2.0.0',
 'flake8>=3.7,<4.0',
 'pygments>=2.4,<3.0',
 'typing_extensions>=3.6,<4.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata']}

entry_points = \
{'flake8.extension': ['WPS = wemake_python_styleguide.checker:Checker'],
 'flake8.report': ['wemake = '
                   'wemake_python_styleguide.formatter:WemakeFormatter']}

setup_kwargs = {
    'name': 'wps-light',
    'version': '0.15.3',
    'description': 'The strictest and most opinionated python linter ever (lighter fork).',
    'long_description': "# wps-light\n\n*wemake-python-styleguide*, but lighter.\n\n```bash\npip install wps-light\n```\n\nThis project is simply a fork of\n[wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide),\n**without these flake8 plugins dependencies**:\n\n- flake8-commas\n- flake8-quotes\n- flake8-comprehensions\n- flake8-docstrings\n- flake8-string-format\n- flake8-bugbear \n- flake8-debugger\n- flake8-isort\n- flake8-eradicate\n- flake8-bandit\n- flake8-broken-line\n- flake8-rst-docstrings\n- pep8-naming\n- darglint\n\nPlease refer to [wemake-python-styleguide's documentation](https://wemake-python-stylegui.de/en/latest/).\n",
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pawamoy/wps-light',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
