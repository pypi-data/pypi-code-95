# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scikeras', 'scikeras.utils']

package_data = \
{'': ['*']}

install_requires = \
['packaging>=0.21,<22.0', 'scikit-learn>=0.22.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3,<4']}

setup_kwargs = {
    'name': 'scikeras',
    'version': '0.4.1',
    'description': 'Scikit-Learn API wrapper for Keras.',
    'long_description': "# Scikit-Learn Wrapper for Keras\n\n[![Build Status](https://github.com/adriangb/scikeras/workflows/Tests/badge.svg)](https://github.com/adriangb/scikeras/actions?query=workflow%3ATests+branch%3Amaster)\n[![Coverage Status](https://codecov.io/gh/adriangb/scikeras/branch/master/graph/badge.svg)](https://codecov.io/gh/adriangb/scikeras)\n[![Docs](https://readthedocs.org/projects/docs/badge/?version=latest)](https://www.adriangb.com/scikeras/)\n\nScikit-Learn compatible wrappers for Keras Models.\n\n## Why SciKeras\n\nSciKeras is derived from and API compatible with `tf.keras.wrappers.scikit_learn`. The original TensorFlow (TF) wrappers are not actively maintained,\nand [will be removed](https://github.com/tensorflow/tensorflow/pull/36137#issuecomment-726271760) in a future release.\n\nAn overview of the advantages and differences as compared to the TF wrappers can be found in our\n[migration](https://www.adriangb.com/scikeras/stable/migration.html) guide.\n\n## Installation\n\nThis package is available on PyPi:\n\n```bash\npip install scikeras\n```\n\nThe only dependencies are `scikit-learn>=0.22` and `TensorFlow>=2.4.0`.\n\nYou will need to manually install TensorFlow; due to TensorFlow's packaging it is not a direct dependency of SciKeras.\nYou can do this by running:\n\n```bash\npip install tensorflow\n```\n\n### Migrating from `tf.keras.wrappers.scikit_learn`\n\nPlease see the [migration](https://www.adriangb.com/scikeras/stable/migration.html) section of our documentation.\n\n## Documentation\n\nDocumentation is available at [https://www.adriangb.com/scikeras/](https://www.adriangb.com/scikeras/).\n\n## Contributing\n\nSee [CONTRIBUTING.md](https://github.com/adriangb/scikeras/blob/master/CONTRIBUTING.md)\n",
    'author': 'Adrian Garcia Badaracco',
    'author_email': '1755071+adriangb@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/adriangb/scikeras',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
