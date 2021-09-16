# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bacs']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'bacs',
    'version': '0.1.1',
    'description': 'Bundle Adjustment For Camera Systems',
    'long_description': '# BACS: Bundle Adjustment For Camera Systems\n\nThis is a Python implementation of BACS, a bundle adjustment for camera systems with points at infinity. It was originally written in Matlab and published by Johannes Schneider, Falko Schindler, Thomas Laebe, and Wolfgang Foerstner in 2012.\n\n## Usage\n\nRun\n\n```bash\npython3 -m pip install bacs\n```\n\nto install the library. \nHave a look at the [extensive doc string](https://github.com/zauberzeug/bacs/blob/main/bacs/bacs.py#L34-L77) for explenation of the parameters.\n\n## Testing / Developing\n\nMake sure you have NumPy and SciPy installed:\n\n```bash\npython3 -m pip install numpy scipy\n```\n\nBy running the provided examples with\n\n```bash\npython3 main.py\n```\n\nyou can verify that bacs is working correctly (eg. no `git diff` in the output data after execution).\n\n## Resources\n\nFurther explanation and visualization can be found on the [BACS project page](https://www.ipb.uni-bonn.de/data-software/bacs/), the corresponding [Matlab demo](https://www.ipb.uni-bonn.de/html/software/bacs/v0.1/demo-v0.1.html) as well as the original [publication](https://www.isprs-ann-photogramm-remote-sens-spatial-inf-sci.net/I-3/75/2012/isprsannals-I-3-75-2012.pdf)\n',
    'author': 'Zauberzeug GmbH',
    'author_email': 'info@zauberzeug.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zauberzeug/bacs',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
