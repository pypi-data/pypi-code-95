# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lanim', 'lanim.examples']

package_data = \
{'': ['*']}

install_requires = \
['pillow>=8.3.2,<9.0.0']

setup_kwargs = {
    'name': 'lanim',
    'version': '0.2.0',
    'description': 'Functional animation library',
    'long_description': "# Lanim\n\nLanim is a library for creating programmatic animations in Python. It's currently in a very early stage.\n\n![Promotional animation](https://decorator-factory.github.io/lanim/docs.gif)\n\nNot everything in the GIF is quite true yet, but soon:tm: it will!\n\nCheck out the [documentation](https://decorator-factory.github.io/lanim/) for a tutorial\n\n\n# Showcase\n\n![Sequence of animations](https://decorator-factory.github.io/lanim/tutorial/how-does-lanim-work/plus-operator.gif)\n![Point moving across a plane](https://decorator-factory.github.io/lanim/tutorial/coordinates/moving-point.gif)\n",
    'author': 'decorator-factory',
    'author_email': '42166884+decorator-factory@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/decorator-factory/lanim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
