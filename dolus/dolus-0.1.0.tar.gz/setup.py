# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['dolus']
install_requires = \
['click-help-colors>=0.9.1,<0.10.0',
 'click>=8.0.1,<9.0.0',
 'numpy>=1.21.2,<2.0.0',
 'opencv-python>=4.5.3,<5.0.0',
 'pafy>=0.5.5,<0.6.0',
 'pyvirtualcam>=0.8.0,<0.9.0',
 'requests>=2.26.0,<3.0.0',
 'youtube_dl>=2021.6.6,<2022.0.0']

entry_points = \
{'console_scripts': ['dolus = dolus:main']}

setup_kwargs = {
    'name': 'dolus',
    'version': '0.1.0',
    'description': 'A command-line interface to put effects on your virtual camera(OBS/Unity/v4l2loopback)',
    'long_description': '# dolus\nA command-line interface to put effects on your virtual camera(OBS/Unity/v4l2loopback)',
    'author': 'Avanindra Chakraborty',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/AvanindraC/dolus',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
