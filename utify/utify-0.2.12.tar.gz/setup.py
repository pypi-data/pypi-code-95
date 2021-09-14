# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['utify']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.2.1,<0.3.0',
 'ipython>=7.10.2,<8.0.0',
 'matplotlib>=3.1.2,<4.0.0',
 'numpy>=1.16.1,<1.19.0',
 'pandas>=1.0.0,<2.0.0',
 'pillow>=6.2.1,<7.0.0',
 'pyarrow>=0.15.1,<0.16.0',
 'requests>=2.22.0,<3.0.0',
 'sqlalchemy>=1.3.12,<2.0.0',
 'tables>=3.6.1,<4.0.0',
 'tqdm>=4.40.2,<5.0.0',
 'wasabi>=0.4.2,<0.5.0']

extras_require = \
{'doc': ['recommonmark>=0.6.0,<0.7.0',
         'sphinx_rtd_theme>=0.4.3,<0.5.0',
         'nbsphinx>=0.5.0,<0.6.0']}

entry_points = \
{'console_scripts': ['utify = utify.cli:main']}

setup_kwargs = {
    'name': 'utify',
    'version': '0.2.12',
    'description': 'Utility Functions for Python',
    'long_description': '# utify: Utility Functions for Python\n\n',
    'author': 'yajiez',
    'author_email': 'yajiez.me@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
