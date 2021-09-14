# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['github_avatars_gallery_generator']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==8.3.2',
 'requests>=2.25.1,<3.0.0',
 'tenacity==7.0.0',
 'tqdm>=4.60.0,<5.0.0']

entry_points = \
{'console_scripts': ['gh-gallery = github_avatars_gallery_generator.main:main']}

setup_kwargs = {
    'name': 'github-avatars-gallery-generator',
    'version': '0.2.0',
    'description': 'Collect the avatars of all contributors of a Github repo and make a gallery',
    'long_description': None,
    'author': 'rexwangcc',
    'author_email': 'rexwangcc@gmail.com',
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
