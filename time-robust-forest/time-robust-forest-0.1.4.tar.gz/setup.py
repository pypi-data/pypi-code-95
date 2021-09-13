# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['time_robust_forest']

package_data = \
{'': ['*']}

install_requires = \
['numpy==1.19.5',
 'pandas==1.1.3',
 'rich>=9.8.2,<11.0.0',
 'scikit-learn==0.23.2',
 'typer[all]>=0.3.2,<0.4.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.6,<5.0']}

entry_points = \
{'console_scripts': ['time-robust-forest = time_robust_forest.__main__:app']}

setup_kwargs = {
    'name': 'time-robust-forest',
    'version': '0.1.4',
    'description': 'Explores time information to train a robust random forest',
    'long_description': '# time-robust-forest\n\n<div align="center">\n\n[![Build status](https://github.com/lgmoneda/time-robust-forest/workflows/build/badge.svg?branch=main&event=push)](https://github.com/lgmoneda/time-robust-forest/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/time-robust-forest.svg)](https://pypi.org/project/time-robust-forest/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/lgmoneda/time-robust-forest/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/lgmoneda/time-robust-forest/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/lgmoneda/time-robust-forest/releases)\n[![License](https://img.shields.io/github/license/lgmoneda/time-robust-forest)](https://github.com/lgmoneda/time-robust-forest/blob/main/LICENSE)\n\n</div>\n\nA Proof of concept model that explores timestamp information to train a random forest with better Out of Distribution generalization power.\n\n## Installation\n\n```bash\npip install -U time-robust-forest\n```\n\n## How to use it\n\nThere are a classifier and a regressor under `time_robust_forest.models`. They follow the sklearn interface, which means you can quickly fit and use a model:\n\n```python\nfrom time_robust_forest.models import TimeForestClassifier\n\nfeatures = ["x_1", "x_2"]\ntime_column = "periods"\ntarget = "y"\n\nmodel.fit(training_data[features + [time_column]], training_data[target])\npredictions = model.predict_proba(test_data[features])[:, 1]\n```\n\nThere are only a few arguments that differ from a traditional Random Forest. two arguments\n\n- time_column: the column from the input dataframe containing the time\nperiods the model will iterate over to find the best splits (default: "period")\n- min_sample_periods: the number of examples in every period the model needs\nto keep while it splits.\n- period_criterion: how the performance in every period is going to be\naggregated. Options: {"avg": average, "max": maximum, the worst case}.\n(default: "avg")\n\n### Make sure you have a good choice for the time column\n\nDon\'t simply use a timestamp column from the dataset, make it discrete before and guarantee there is a reasonable amount of data points in every period. Example: use year if you have 3+ years of data. Notice the choice to make it discrete becomes a modeling choice you can optimize.\n\n## License\n\n[![License](https://img.shields.io/github/license/lgmoneda/time-robust-forest)](https://github.com/lgmoneda/time-robust-forest/blob/main/LICENSE)\n\nThis project is licensed under the terms of the `BSD-3` license. See [LICENSE](https://github.com/lgmoneda/time-robust-forest/blob/main/LICENSE) for more details.\n\n## Citation\n\n```\n@misc{time-robust-forest,\n  author = {Moneda, Luis},\n  title = {Time Robust Forest model},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/lgmoneda/time-robust-forest}}\n}\n```\n',
    'author': 'lgmoneda',
    'author_email': 'lgmoneda@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lgmoneda/time-robust-forest',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.3,<4.0.0',
}


setup(**setup_kwargs)
