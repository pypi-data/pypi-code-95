# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['replay',
 'replay.metrics',
 'replay.models',
 'replay.scenarios',
 'replay.scenarios.two_stages',
 'replay.splitters']

package_data = \
{'': ['*']}

install_requires = \
['lightautoml',
 'lightfm',
 'llvmlite',
 'nevergrad',
 'numba',
 'numpy<1.21',
 'optuna',
 'pandas',
 'psutil',
 'pyspark',
 'pytorch-ignite',
 'scikit-learn',
 'scipy',
 'seaborn',
 'statsmodels',
 'torch']

setup_kwargs = {
    'name': 'replay-rec',
    'version': '0.6.0',
    'description': 'RecSys Library',
    'long_description': '# RePlay\n\nRePlay is a library providing tools for all stages of creating a recommendation system, from data preprocessing to model evaluation and comparison.\n\nRePlay uses PySpark to handle big data.\n\nYou can\n\n- Filter and split data\n- Train models\n- Optimize hyper parameters\n- Evaluate predictions with metrics\n- Combine predictions from different models\n- Create a two-level model\n\n\n## Docs\n\n[Documentation](https://sberbank-ai-lab.github.io/RePlay/)\n\n\n### Installation\n\nUse Linux machine with Python 3.6+ and Java 8+. \n\n```bash\npip install replay-rec\n```\n\nIt is preferable to use a virtual environment for your installation.\n',
    'author': 'Boris Shminke',
    'author_email': 'Shminke.B.A@sberbank.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sberbank-ai-lab/RePlay',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
