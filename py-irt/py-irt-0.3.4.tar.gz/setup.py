# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_irt', 'py_irt.models']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.20.3,<2.0.0',
 'pandas>=1.1,<2.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyro-ppl>=1.6.0,<2.0.0',
 'rich>=9.3.0,<10.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.6.3,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['py-irt = py_irt.cli:app']}

setup_kwargs = {
    'name': 'py-irt',
    'version': '0.3.4',
    'description': 'Bayesian IRT models in Python',
    'long_description': '[![Build Status](https://travis-ci.com/nd-ball/py-irt.svg?branch=master)](https://travis-ci.com/nd-ball/py-irt)\n[![codecov.io](https://codecov.io/gh/nd-ball/py-irt/coverage.svg?branch=master)](https://codecov.io/gh/nd-ball/py-irt)\n\n# py-irt\n\nBayesian IRT models in Python\n\n## Overview\n\nThis repository includes code for fitting Item Response Theory (IRT) models using variational inference.\n\nAt present, the one parameter logistic (1PL) model, aka Rasch model, two parameter logistic model (2PL) and four parameter logistic model (4PL) have been implemented.\nThe user can specify whether vague or hierarchical priors are used.\nThe three-parameter logistic model is in the pipeline and will be added when available.\n\n## License\n\npy-irt is licensed under the [MIT license](https://opensource.org/licenses/MIT).\n\n## Installation\n\npy-irt is now available on PyPi!\n\n### Pre-reqs\n\n1. Install [PyTorch](https://pytorch.org/get-started/locally/).\n2. Install [Pyro](https://pyro.ai/)\n3. Install py-irt:\n\n```shell\npip install py-irt\n```\n\nOR\n\n```shell\ngit clone https://github.com/nd-ball/py-irt.git\ncd py-irt\npip install -r requirements.txt\n```\n\n## Usage\n\nOnce you install from PyPI, you can use the following command to fit an IRT\nmodel on the scored predictions of a dataset. For example, if you were to run py-irt with the 4PL model on the scored predictions of different transformer models on the SQuAD dataset, you\'d do this:\n`py-irt train 4pl ~/path/to/dataset/eg/squad.jsonlines /path/to/output/eg/test-4pl/`\n\n## FAQ\n\n1. What kind of output should I expect on running the command to train an IRT model?\n\nYou should see something like this when you run the command given above:\n![image](https://user-images.githubusercontent.com/40918514/123986740-3eccd100-d9cf-11eb-8e58-ba5ad6c977ce.png)\n\n2. I tried installing py-irt using pip from PyPI. But when I try to run the command `py-irt train 4pl ~/path/to/dataset/eg/squad.jsonlines /path/to/output/eg/test-4pl/`, I get an error that says `bash: py-irt: command not found`. How do I fix this?\n\nThe CLI interface was implemented in PyPi version 0.2.1. If you are getting this error try updating py-irt:\n\n`pip install --upgrade py-irt`\n\nAlternatively, you can install the latest version from github:\n\n```shell\ngit clone https://github.com/nd-ball/py-irt.git\ncd py-irt\nmv ~/py-irt/py_irt/cli.py ~/py-irt/\npython cli.py train 4pl ~/path/to/dataset/eg/squad.jsonlines /path/to/output/eg/test-4pl/\n```\n\n3. How do I evaluate a trained IRT model?\n\nIf you have already trained an IRT model you can use the following command:\n\n`py-irt evaluate 4pl ~/path/to/data/best_parameters.json ~/path/to/data/test_pairs.jsonlines /path/to/output/eg/test-4pl/`\n\nWhere `test_pairs.jsonlines` is a jsonlines file with the following format:\n\n```\n{"subject_id": "ken", "item_id": "q1"}\n{"subject_id": "ken", "item_id": "q2"}\n{"subject_id": "burt", "item_id": "q1"}\n{"subject_id": "burt", "item_id": "q3"}\n```\n\nIf you would like to both train and evaluate a model you can use the following command:\n\n`py-irt train_and_evaluate 4pl ~/path/to/data/squad.jsonlines /path/to/output/eg/test-4pl/`\n\nBy default this will train a model with 90% of the provided data and evaluate with the remaining 10%.\nTo change this behavior you can add `--evaluation all` to the command above. \nThe model will train and evaluate against all of the data.\n\n## Citations\n\nIf you use this code, please consider citing the following paper:\n\n```shell\n@inproceedings{lalor2019emnlp,\n  author    = {Lalor, John P and Wu, Hao and Yu, Hong},\n  title     = {Learning Latent Parameters without Human Response Patterns: Item Response Theory with Artificial Crowds},\n  year      = {2019},\n  booktitle = {Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing},\n}\n```\n\nImplementation is based on the following paper:\n\n```shell\n@article{natesan2016bayesian,\n  title={Bayesian prior choice in IRT estimation using MCMC and variational Bayes},\n  author={Natesan, Prathiba and Nandakumar, Ratna and Minka, Tom and Rubright, Jonathan D},\n  journal={Frontiers in psychology},\n  volume={7},\n  pages={1422},\n  year={2016},\n  publisher={Frontiers}\n}\n```\n\n## Contributing\n\nThis is research code. Pull requests and issues are welcome!\n\n## Questions?\n\nLet me know if you have any requests, bugs, etc.\n\nEmail: john.lalor@nd.edu\n',
    'author': 'John P. Lalor',
    'author_email': 'john.lalor@nd.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nd-ball/py-irt/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
