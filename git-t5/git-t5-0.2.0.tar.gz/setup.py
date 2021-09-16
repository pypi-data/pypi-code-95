# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_t5',
 'git_t5.cli',
 'git_t5.cli.conf',
 'git_t5.core',
 'git_t5.core.configs',
 'git_t5.data',
 'git_t5.tests',
 'git_t5.utils']

package_data = \
{'': ['*'],
 'git_t5.cli.conf': ['data/*',
                     'dataset/*',
                     'logger/*',
                     'model/*',
                     'optimizer/*',
                     'optimizer/scheduler/*',
                     'tokenizer/*',
                     'tokenizer_trainer/*',
                     'tokenizer_trainer/tokenizer/*',
                     'trainer/*',
                     'training/*']}

install_requires = \
['datasets>=1.11.0,<2.0.0',
 'flax>=0.3.4,<0.4.0',
 'hydra-core>=1.1.1,<2.0.0',
 'jax>=0.2.19,<0.3.0',
 'more-itertools>=8.8.0,<9.0.0',
 'optax>=0.0.9,<0.0.10',
 'sacrebleu>=1.5.1,<2.0.0',
 'torch>=1.9.0,<2.0.0',
 'transformers>=4.10.0,<5.0.0',
 'wandb>=0.12.1,<0.13.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.10.0.2,<4.0.0.0']}

entry_points = \
{'console_scripts': ['gt5-train-model = git_t5.cli.train_model:main',
                     'gt5-train-tokenizer = git_t5.cli.train_tokenizer:main']}

setup_kwargs = {
    'name': 'git-t5',
    'version': '0.2.0',
    'description': 'Open source machine learning framework for training T5 models on source code in JAX/Flax.',
    'long_description': '# git-t5',
    'author': 'mozharovsky',
    'author_email': 'mozharovsky@live.com',
    'maintainer': 'mozharovsky',
    'maintainer_email': 'mozharovsky@live.com',
    'url': 'https://github.com/formermagic/git-t5',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
