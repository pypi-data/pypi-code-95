# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydra_slayer']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'hydra-slayer',
    'version': '0.2.0',
    'description': 'A framework for elegantly configuring complex applications',
    'long_description': '<img src="docs/_static/slayer.png" width="198" align="right">\n\n# Hydra Slayer\n\n[![build](https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml/badge.svg)](https://github.com/catalyst-team/hydra-slayer/actions/workflows/build.yml)\n[![Pipi version](https://img.shields.io/pypi/v/hydra-slayer)](https://pypi.org/project/hydra-slayer/)\n[![Python Version](https://img.shields.io/pypi/pyversions/hydra-slayer)](https://pypi.org/project/hydra-slayer/)\n[![License](https://img.shields.io/github/license/catalyst-team/hydra-slayer)](LICENSE)\n[![Slack](https://img.shields.io/badge/slack-join_chat-brightgreen.svg)](https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw)\n\n**Hydra Slayer** is a 4th level spell in the School of Fire Magic.\nDepending of the level of expertise in fire magic,\nslayer spell increases attack of target troop by 8 against\nbehemoths, dragons, hydras, and other creatures.\n\nWhat is more, it also allows configuring of complex applications just by config and few lines of code.\n\n---\n\n## Installation\nUsing pip you can easily install the latest release version [PyPI](https://pypi.org/):\n\n```sh\npip install hydra-slayer\n```\n\n## Example\n```yaml title="dataset.yaml"\ndataset:\n  _target_: torchvision.datasets.CIFAR100\n  root: ./data\n  train: false\n  download: true\n```\n\n```python title="run.py"\nimport hydra_slayer\nimport yaml\n\nwith open("dataset.yaml") as stream:\n    raw_config = yaml.safe_load(stream)\n\nconfig = hydra_slayer.get_from_params(**raw_config)\nconfig["dataset"]\n# Dataset CIFAR100\n#     Number of datapoints: 10000\n#     Root location: ./data\n#     Split: Test\n```\n\nPlease check [documentation](https://catalyst-team.github.io/hydra-slayer/master/pages/examples) for more examples.\n\n## Documentation\nFull documentation for the project is available at https://catalyst-team.github.io/hydra-slayer\n\n## Communication\n- GitHub Issues: Bug reports, feature requests, install issues, RFCs, thoughts, etc.\n- Slack: The [Catalyst Slack](https://join.slack.com/t/catalyst-team-core/shared_invite/zt-d9miirnn-z86oKDzFMKlMG4fgFdZafw) hosts a primary audience of moderate to experienced Hydra-Slayer (and Catalyst) users and developers for general chat, online discussions, collaboration, etc.\n- Email: Feel free to use [feedback@catalyst-team.com](mailto:feedback@catalyst-team.com) as an additional channel for feedback.\n\n## Citation\nPlease use this bibtex if you want to cite this repository in your publications:\n\n    @misc{catalyst,\n        author = {Sergey Kolesnikov and Yauheni Kachan},\n        title = {Hydra-Slayer},\n        year = {2021},\n        publisher = {GitHub},\n        journal = {GitHub repository},\n        howpublished = {\\url{https://github.com/catalyst-team/hydra-slayer}},\n    }\n',
    'author': 'Sergey Kolesnikov',
    'author_email': 'scitator@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://catalyst-team.github.io/hydra-slayer/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
