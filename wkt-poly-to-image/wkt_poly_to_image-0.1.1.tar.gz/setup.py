# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wkt_poly_to_image']

package_data = \
{'': ['*']}

install_requires = \
['Shapely>=1.7.1,<2.0.0', 'numpy>=1.21.2,<2.0.0', 'rasterio>=1.2.8,<2.0.0']

entry_points = \
{'console_scripts': ['test = scripts:test']}

setup_kwargs = {
    'name': 'wkt-poly-to-image',
    'version': '0.1.1',
    'description': 'A python library to convert wkt polygons into raster images.',
    'long_description': '',
    'author': 'Bronson Brown-deVost',
    'author_email': 'bronsonbdevost@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/bronsonbdevost/wkt_poly_to_image',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
