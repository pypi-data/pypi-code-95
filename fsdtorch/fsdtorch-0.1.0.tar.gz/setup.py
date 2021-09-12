# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fsdtorch']

package_data = \
{'': ['*']}

install_requires = \
['gdown>=3.13.0,<4.0.0',
 'onnx>=1.10.1,<2.0.0',
 'onnxruntime-gpu>=1.8.1,<2.0.0',
 'opencv-contrib-python>=4.5.3,<5.0.0']

setup_kwargs = {
    'name': 'fsdtorch',
    'version': '0.1.0',
    'description': 'Face shape detector in pytorch that works with pretrained networks',
    'long_description': None,
    'author': 'Alper',
    'author_email': 'itsc0508@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
