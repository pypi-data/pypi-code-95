# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nbox', 'nbox.framework']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.2,<9.0.0',
 'numpy>=1.19.5,<2.0.0',
 'randomname>=0.1.3,<0.2.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.7.0,<11.0.0']

setup_kwargs = {
    'name': 'nbox',
    'version': '0.1.7',
    'description': 'ML Inference 🥶',
    'long_description': None,
    'author': 'NBX Research',
    'author_email': 'research@nimblebox.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
