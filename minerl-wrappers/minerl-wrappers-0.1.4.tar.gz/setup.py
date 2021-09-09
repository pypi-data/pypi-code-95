# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minerl_wrappers',
 'minerl_wrappers.core',
 'minerl_wrappers.pfrl',
 'minerl_wrappers.pfrl.wrappers']

package_data = \
{'': ['*'], 'minerl_wrappers': ['data/*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'gym>=0.19.0,<0.20.0',
 'minerl==0.4.1a2',
 'numpy>=1.21.0,<2.0.0',
 'opencv-python>=4.5.3,<5.0.0']

setup_kwargs = {
    'name': 'minerl-wrappers',
    'version': '0.1.4',
    'description': 'minerl-wrappers compiles common wrappers and standardizes code for reproducibility in the MineRL environment!',
    'long_description': '# minerl-wrappers\n\n![Tests](https://github.com/minerl-wrappers/minerl-wrappers/actions/workflows/workflow.yaml/badge.svg)\n[![codecov](https://codecov.io/gh/minerl-wrappers/minerl-wrappers/branch/main/graph/badge.svg?token=0BPxXISonq)](https://codecov.io/gh/minerl-wrappers/minerl-wrappers)\n![PyPI](https://img.shields.io/pypi/v/minerl-wrappers)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/minerl-wrappers)\n![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/minerl-wrappers)\n\n`minerl-wrappers` compiles common wrappers and standardizes code for reproducibility in the [MineRL environment](https://minerl.readthedocs.io/en/latest/index.html)!\n\n# Currently Supported Environments\n- MineRL Basic Environments\n  - [`MineRLTreechop-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerltreechop-v0)\n  - [`MineRLNavigate-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigate-v0)\n  - [`MineRLNavigateDense-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigatedense-v0)\n  - [`MineRLNavigateExtreme-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigateextreme-v0)\n  - [`MineRLNavigateExtremeDense-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigateextremedense-v0)\n  - [`MineRLObtainDiamond-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtaindiamond-v0)\n  - [`MineRLObtainDiamondDense-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtaindiamonddense-v0)\n  - [`MineRLObtainIronPickaxe-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtainironpickaxe-v0)\n  - [`MineRLObtainIronPickaxeDense-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtainironpickaxedense-v0)\n- MineRL Diamond Competition Environments\n  - [`MineRLTreechopVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerltreechopvectorobf-v0)\n  - [`MineRLNavigateVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigatevectorobf-v0)\n  - [`MineRLNavigateDenseVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigatedensevectorobf-v0)\n  - [`MineRLNavigateExtremeVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigateextremevectorobf-v0)\n  - [`MineRLNavigateExtremeDenseVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlnavigateextremedensevectorobf-v0)\n  - [`MineRLObtainDiamondVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtaindiamondvectorobf-v0)\n  - [`MineRLObtainDiamondDenseVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtaindiamonddensevectorobf-v0)\n  - [`MineRLObtainIronPickaxeVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtainironpickaxevectorobf-v0)\n  - [`MineRLObtainIronPickaxeDenseVectorObf-v0`](https://minerl.readthedocs.io/en/latest/environments/index.html#minerlobtainironpickaxedensevectorobf-v0)\n\n# Wappers\n- pfrl wrappers: an assortment of wrappers ported over from the [2020 PfN minerl baselines](https://github.com/minerllabs/baselines/tree/master/2020)\nand [2019 PfN minerl baselines](https://github.com/minerllabs/baselines/tree/master/2019)\n  - Supports Basic Environments for 2019 and Diamond Competition Environments for 2020\n- diamond wrappers: updated wrappers for the 2021 MineRL Diamond Competition Environments\n\n## Wrap arguments\nFor documentation see wrapper files:  \n[pfrl_2019_wrappers.py](https://github.com/minerl-wrappers/minerl-wrappers/blob/main/minerl_wrappers/pfrl_2019_wrappers.py)  \n[pfrl_2020_wrappers.py](https://github.com/minerl-wrappers/minerl-wrappers/blob/main/minerl_wrappers/pfrl_2020_wrappers.py)\n[diamond_wrappers.py](https://github.com/minerl-wrappers/minerl-wrappers/blob/main/minerl_wrappers/diamond_wrappers.py)\n\n# Requirements\n- Java JDK 8\n- Python 3.7+\n- `minerl==0.4.1`\n\n# Install\n\nMake sure you have Java JDK 8 installed as the only Java version for MineRL.\n\nInstall with pip from pypi:\n```bash\npip install minerl-wrappers\n```\n\nInstall directly from git:\n```bash\npip install git+https://github.com/minerl-wrappers/minerl-wrappers.git\n```\n\n## Clone and Install\n```bash\ngit clone https://github.com/minerl-wrappers/minerl-wrappers.git\ncd minerl-wrappers\n```\n\n### Use your own virtual environment\n\n#### virtualenv\nInstalled Python 3.7+\n```bash\npython3 -m virtualenv venv\nsource venv/bin/activate\n```\n\n#### conda\nInstall Anaconda or Miniconda\n```bash\nconda create --name minerl-wrappers python=3.7\nconda activate minerl-wrappers\n```\n\n### Install dependencies\n1. Install dependencies with pip:\n  ```bash\n  # install fixed requirements\n  pip install -r requirements.txt\n  # set the minerl-wrappers module for imports\n  export PYTHONPATH=$PYTHONPATH:$(pwd)\n  ```\n2. Install dependencies with [`poetry`](https://python-poetry.org/docs/#installation) into your virtual environment:\n  ```bash\n  # this also installs minerl-wrappers as a package\n  poetry install --no-dev\n  ```\n\n# Use\n\nTo quickly test out the wrappers try:\n```python\nimport gym\nimport minerl\nfrom minerl_wrappers import wrap\n\nenv = gym.make("MineRLObtainDiamondDenseVectorObf-v0")\nenv = wrap(env) # plug this into your rl algorithm\n```\n\nChange which wrappers to apply by supplying config arguments:\n```python\nconfig = {\n  "diamond": True,\n  "diamond_config": {\n    "frame_skip": 4,\n    "frame_stack": 4,\n  }\n}\nenv = wrap(env, **config)\n```\n\n# Contributing\nIt is highly encouraged to contribute wrappers that worked well for you!\nJust create a [Pull Request](https://github.com/minerl-wrappers/minerl-wrappers/pulls) on this repository, \nand we\'ll work together to get it merged!\nRead [`README-DEV.md`](https://github.com/minerl-wrappers/minerl-wrappers/blob/main/README-DEV.md) for contributing guidelines and more details!\n',
    'author': 'Julius Frost',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minerl-wrappers/minerl-wrappers/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
