# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['banded_matrices']

package_data = \
{'': ['*'],
 'banded_matrices': ['cc/*',
                     'cc/include/banded_matrices/*',
                     'cc/src/banded_matrices/*',
                     'cc/test/*']}

install_requires = \
['cmake>=3.18.0,<3.19.0',
 'importlib_metadata>=1.6,<2.0',
 'numpy>=1.18.0,<2.0.0',
 'tensorflow>=2.4.0,<2.5.0']

setup_kwargs = {
    'name': 'banded-matrices',
    'version': '0.0.6',
    'description': 'Native (C++) implementation of Banded Matrices for TensorFlow',
    'long_description': '# Banded Matrices\n\n## Overview\n\nA library providing C++ linear algebra operators (matmul, solve, ...) dedicated to banded matrices and a [TensorFlow](https://www.tensorflow.org/) interface.\nThis extends the set of existing TensorFlow operators which as of August 2021 only include `banded_triangular_solve`.\n\nDetails on the implemented operators may be found in Durrande et al.:\n"[Banded Matrix Operators for Gaussian Markov Models in the Automatic Differentiation Era](http://proceedings.mlr.press/v89/durrande19a.html)", and in Adam et al.: "[Doubly Sparse Variational Gaussian Processes](http://proceedings.mlr.press/v108/adam20a.html)" \n\n\n## Installation\n\n### For users\n\nTo install the latest (stable) release of the toolbox from [PyPI](https://pypi.org/), use `pip`:\n```bash\n$ pip install banded_matrices\n```\n\n### For contributors\n\nThis project uses [Poetry](https://python-poetry.org/docs) to\nmanage dependencies in a local virtual environment. To install Poetry, [follow the\ninstructions in the Poetry documentation](https://python-poetry.org/docs/#installation).\n\nTo install this project in editable mode, run the commands below from the root directory of the\n`banded_matrices` repository.\n\n```bash\npoetry install\n```\n\nThis command creates a virtual environment for this project\nin a hidden `.venv` directory under the root directory.\n\nYou must also run the `poetry install` command to install updated dependencies when\nthe `pyproject.toml` file is updated, for example after a `git pull`.\n\n**NOTE:** Unlike most other Python packages, by installing the `banded_matrices` package\nfrom source you will trigger a compilation of the C++ TensorFlow ops library. This means that\nrunning `poetry install` can take a while - in the order of 5 minutes, depending on the machine\nyou are installing onto.\n  \n#### Known issues\n\nPoetry versions above `1.0.9` don\'t get along (for now) with Ubuntu 18.04, if you have this OS, \nyou will likely need to install version `1.0.9`. This can be done with the following command\n\n```bash\nwget https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py\nPOETRY_VERSION=1.0.9 python get-poetry.py \n```\n\nRecommended Poetry installation might pick up Python 2 if it is used by the operating system, \nthis will cause problems with looking up libraries and sorting out dependencies if your \nlibrary uses Python 3. If this happens, poetry has a command you can use to instruct it to use \na correct Python version (here assuming you want to use python3.7 and have it installed on your \nsystem - note that `python3.7-venv` package will need to be installed as well). \n\n```bash\npoetry env use python3.7 && poetry install\n```\n\nThe `poetry install` command might fail to install certain Python packages \n(those that use the \'manylinux2010\' platform tag), if the version of\n`pip` installed when creating the Poetry virtual environment is too old.\nUnfortunately the version of `pip` used when creating the virtual environment is vendored with each\nPython version, and it is not possible to update this.\n\nThe solution is to update the version of `pip` in the Poetry virtual environment after the initial\ninstall fails, and then reattempt the installation. To do this, use the command:\n\n```bash\npoetry install || { poetry run pip install -U pip==20.0.2 && poetry install; }\n```\n\n## Running the tests\n\nRun these commands from the root directory of this repository. \nTo run the full Python test suite, including pylint and Mypy, run: \n\n```bash\npoetry run task test\n```\n\nAlternatively, you can run just the unit tests, starting with the failing tests and exiting after\nthe first test failure:\n\n```bash\npoetry run task quicktest\n```\n\nTo run linting of the C++ code (using cpplint), run:\n\n```bash\npoetry run task cpplint\n```\n\n**NOTE:** Running the tests requires\nthat the project virtual environment has been updated. See [Installation](#Installation).\n\n## The Secondmind Labs Community\n\n### Getting help\n\n**Bugs, feature requests, pain points, annoying design quirks, etc:**\nPlease use [GitHub issues](https://github.com/secondmind-labs/banded_matrices/issues/) to flag up bugs/issues/pain points, suggest new features, and discuss anything else related to the use of banded_matrices that in some sense involves changing the banded_matrices code itself. We positively welcome comments or concerns about usability, and suggestions for changes at any level of design. We aim to respond to issues promptly, but if you believe we may have forgotten about an issue, please feel free to add another comment to remind us.\n\n### Slack workspace\n\nWe have a public [Secondmind Labs slack workspace](https://secondmind-labs.slack.com/). Please use this [invite link](https://join.slack.com/t/secondmind-labs/shared_invite/zt-ph07nuie-gMlkle__tjvXBay4FNSLkw) and join the #banded_matrices channel, whether you\'d just like to ask short informal questions or want to be involved in the discussion and future development of banded_matrices.\n\n\n### Contributing\n\nAll constructive input is very much welcome. For detailed information, see the [guidelines for contributors](CONTRIBUTING.md).\n\n\n### Maintainers\n\nBanded_matrices was originally created at [Secondmind Labs](https://www.secondmind.ai/labs/) and is now maintained by (in alphabetical order)\n[Vincent Adam](https://vincentadam87.github.io/),\n[Artem Artemev](https://github.com/awav/).\n**We are grateful to [all contributors](CONTRIBUTORS.md) who have helped shape banded_matrices.**\n\nBanded_matrices is an open source project. If you have relevant skills and are interested in contributing then please do contact us (see ["The Secondmind Labs Community" section](#the-secondmind-labs-community) above).\n\nWe are very grateful to our Secondmind Labs colleagues, maintainers of [GPflow](https://github.com/GPflow/GPflow), [GPflux](https://github.com/secondmind-labs/GPflux), [Trieste](https://github.com/secondmind-labs/trieste) and [Bellman](https://github.com/Bellman-devs/bellman), for their help with creating contributing guidelines, instructions for users and open-sourcing in general.\n\n',
    'author': 'Banded matrices contributors',
    'author_email': 'labs@secondmind.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/secondmind-labs/banded_matrices',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
