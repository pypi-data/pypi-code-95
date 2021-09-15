# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trim21_flexget_plugins', 'trim21_flexget_plugins.modify']

package_data = \
{'': ['*']}

entry_points = \
{'FlexGet.plugins': ['magnet_add_dn = '
                     'trim21_flexget_plugins.modify.magnet_add_dn.PluginMagnetAddDownloadName']}

setup_kwargs = {
    'name': 'trim21-flexget-plugins',
    'version': '0.0.1',
    'description': 'A set of plugins for flexget',
    'long_description': '![PyPI](https://img.shields.io/pypi/v/trim21-flexget-plugins)\n\n```bash\npip install trim21-flexget-plugins\n```\n\n# Add Download Name to Magnet url\n\n```yaml\ntasks:\n  task name 1:\n    magnet_add_dn: true\n```\n',
    'author': 'Trim21',
    'author_email': 'i@trim21.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Trim21/flexget-plugins',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
