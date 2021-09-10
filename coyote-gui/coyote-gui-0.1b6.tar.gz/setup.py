# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rkviewer',
 'rkviewer.canvas',
 'rkviewer.plugin',
 'rkviewer.resources',
 'rkviewer_plugins']

package_data = \
{'': ['*']}

install_requires = \
['commentjson>=0.9.0,<0.10.0',
 'marshmallow-polyfield>=5.10,<6.0',
 'marshmallow>=3.11.1,<4.0.0',
 'sortedcontainers>=2.3.0,<3.0.0',
 'wxPython==4.1.1']

extras_require = \
{':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.8,<0.9'],
 'sbml': ['tellurium>=2.2.0,<3.0.0',
          'sbml2matlab==1.2.3',
          'networkx>=2.5.1,<3.0.0',
          'simplesbml>=2.2.0,<3.0.0',
          'python-libsbml>=5.18.0,<6.0.0',
          'pandas>=1.3.0,<2.0.0']}

entry_points = \
{'console_scripts': ['coyote = rkviewer.main:main']}

setup_kwargs = {
    'name': 'coyote-gui',
    'version': '0.1b6',
    'description': 'Extensible visualization and editing tool for reaction networks.',
    'long_description': None,
    'author': 'Gary Geng',
    'author_email': 'xiaog3@uw.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
