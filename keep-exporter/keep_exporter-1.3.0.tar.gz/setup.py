# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['keep_exporter']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'click-config-file>=0.6.0,<0.7.0',
 'click>=8.0.1,<9.0.0',
 'gkeepapi>=0.13.4,<0.14.0',
 'mdutils>=1.3.0,<2.0.0',
 'pathvalidate>=2.3.2,<3.0.0',
 'python-frontmatter>=0.5.0,<0.6.0']

entry_points = \
{'console_scripts': ['keep_export = keep_exporter.cli:main']}

setup_kwargs = {
    'name': 'keep-exporter',
    'version': '1.3.0',
    'description': 'Google Keep note exporter utility',
    'long_description': None,
    'author': 'Nathan Beals',
    'author_email': 'ndbeals@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
