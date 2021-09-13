# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ztrack',
 'ztrack.gui',
 'ztrack.gui.utils',
 'ztrack.tracking',
 'ztrack.tracking.eye',
 'ztrack.tracking.tail',
 'ztrack.utils']

package_data = \
{'': ['*'], 'ztrack.gui': ['img/*']}

install_requires = \
['PyQt5>=5.15.4,<6.0.0',
 'click>=8.0.1,<9.0.0',
 'decord>=0.6.0,<0.7.0',
 'matplotlib>=3.4.2,<4.0.0',
 'opencv-python>=4.5.2,<5.0.0',
 'pandas>=1.3.0,<2.0.0',
 'pyqtgraph>=0.12.2,<0.13.0',
 'qtmodern>=0.2.0,<0.3.0',
 'scikit-image>=0.18.2,<0.19.0',
 'tables>=3.6.1,<4.0.0',
 'tqdm>=4.61.2,<5.0.0']

extras_require = \
{'dev': ['black',
         'isort',
         'flake8',
         'mypy',
         'pydata-sphinx-theme',
         'sphinx',
         'sphinx-autodoc-typehints']}

entry_points = \
{'console_scripts': ['ztrack = ztrack.cli:main']}

setup_kwargs = {
    'name': 'ztrack',
    'version': '0.2.1',
    'description': '',
    'long_description': '[![PyPI version](https://badge.fury.io/py/ztrack.svg)](https://pypi.python.org/pypi/ztrack)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ztrack.svg)](https://pypi.python.org/pypi/ztrack)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n# ztrack\n\nToolbox for zebrafish pose estimation.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install ztrack.\n\n```bash\npip install ztrack\n```\n',
    'author': 'Ka Chung Lam',
    'author_email': 'kclamar@connect.ust.hk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kclamar/ztrack',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
