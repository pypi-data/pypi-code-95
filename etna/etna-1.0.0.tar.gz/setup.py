# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['etna',
 'etna.analysis',
 'etna.analysis.outliers',
 'etna.datasets',
 'etna.metrics',
 'etna.model_selection',
 'etna.models',
 'etna.transforms']

package_data = \
{'': ['*']}

install_requires = \
['catboost>=0.25,<0.26',
 'dill>=0.3.4,<0.4.0',
 'numba>=0.53.1,<0.54.0',
 'pandas>=1,<2',
 'prophet>=1.0,<2.0',
 'pytorch-forecasting==0.8.5',
 'ruptures==1.1.3',
 'scikit-learn>=0.24.1,<0.25.0',
 'seaborn>=0.11.1,<0.12.0',
 'statsmodels>=0.12.2,<0.13.0',
 'toml>=0.10.2,<0.11.0',
 'torch>=1.8.0,<1.9.0']

extras_require = \
{'all': ['sphinx-mathjax-offline>=0.0.1,<0.0.2',
         'nbsphinx>=0.8.2,<0.9.0',
         'Sphinx>=3.5.1,<4.0.0',
         'numpydoc>=1.1.0,<2.0.0',
         'sphinx-rtd-theme>=0.5.1,<0.6.0',
         'myst-parser>=0.14.0,<0.15.0',
         'pytest>=6.2,<7.0',
         'coverage>=5.4,<6.0',
         'pytest-cov>=2.11.1,<3.0.0',
         'black==19.3b0',
         'isort>=5.8.0,<6.0.0',
         'flake8>=3.9.2,<4.0.0',
         'pep8-naming>=0.11.1,<0.12.0',
         'flake8-docstrings>=1.6.0,<2.0.0'],
 'docs': ['sphinx-mathjax-offline>=0.0.1,<0.0.2',
          'nbsphinx>=0.8.2,<0.9.0',
          'Sphinx>=3.5.1,<4.0.0',
          'numpydoc>=1.1.0,<2.0.0',
          'sphinx-rtd-theme>=0.5.1,<0.6.0',
          'myst-parser>=0.14.0,<0.15.0'],
 'style': ['black==19.3b0',
           'isort>=5.8.0,<6.0.0',
           'flake8>=3.9.2,<4.0.0',
           'pep8-naming>=0.11.1,<0.12.0',
           'flake8-docstrings>=1.6.0,<2.0.0'],
 'tests': ['pytest>=6.2,<7.0',
           'coverage>=5.4,<6.0',
           'pytest-cov>=2.11.1,<3.0.0']}

setup_kwargs = {
    'name': 'etna',
    'version': '1.0.0',
    'description': 'ETNA is the first python open source framework of Tinkoff.ru AI Center. It is designed to make working with time series simple, productive, and fun.',
    'long_description': '# ETNA Time Series Library\n\n[![Pipi version](https://img.shields.io/pypi/v/catalyst.svg)](https://pypi.org/project/etna-ts/)\n[![PyPI Status](https://static.pepy.tech/personalized-badge/etna-ts?period=total&units=international_system&left_color=grey&right_color=green&left_text=Downloads)](https://pepy.tech/project/etna-ts)\n\n[![Telegram](https://img.shields.io/badge/channel-telegram-blue)](https://t.me/etna_support)\n\n\n[Homepage](https://etna.tinkoff.ru) |\n[Documentation](https://etna-docs.netlify.app/) |\n[Tutorials](https://github.com/tinkoff-ai/etna-ts/tree/master/examples) | \n[Contribution Guide](https://github.com/tinkoff-ai/etna-ts/blob/master/CONTRIBUTING.md) |\n[Release Notes](https://github.com/tinkoff-ai/etna-ts/releases)\n\nETNA is an easy-to-use time series forecasting framework. \nIt includes built in toolkits for time series preprocessing, feature generation, \na variety of predictive models with unified interface - from classic machine learning\nto SOTA neural networks, models combination methods and smart backtesting.\nETNA is designed to make working with time series simple, productive, and fun. \n\nETNA is the first python open source framework of \n[Tinkoff.ru](https://www.tinkoff.ru/eng/)\nArtificial Intelligence Center. \nThe library started as an internal product in our company - \nwe use it in over 10+ projects now, so we often release updates. \nContributions are welcome - check our [Contribution Guide](https://github.com/tinkoff-ai/etna-ts/blob/master/CONTRIBUTING.md).\n\n\n\n## Installation \n\nETNA is on [PyPI](https://pypi.org/project/etna-ts/0.0.1/), so you can use `pip` to install it.\n\n```bash\npip install --upgrade pip\npip install etna-ts\n```\n\n\n## Get started \nHere\'s some example code for a quick start.\n```python\nimport pandas as pd\nfrom etna.datasets.tsdataset import TSDataset\nfrom etna.models import ProphetModel\n\n# Read the data\ndf = pd.read_csv("example_dataset.csv")\ndf["timestamp"] = pd.to_datetime(df["timestamp"])\n\n# Create a TSDataset\ndf = TSDataset.to_dataset(df)\nts = TSDataset(df,freq=\'1d\')\n\n# Choose a horizon\nHORIZON = 8\n\n# Fit the model\nmodel = ProphetModel()\nmodel.fit(ts)\n\n# Make the forecast\nfuture_ts = ts.make_future(HORIZON)\nforecast_ts = model.forecast(future_ts)\n```\n\n## Tutorials\nWe have also prepared a set of tutorials for an easy introduction:\n\n#### 01. [Get started](https://github.com/tinkoff-ai/etna-ts/tree/master/examples/get_started.ipynb)\n- Creating TSDataset and time series plotting \n- Forecast single time series - Simple forecast, Prophet, Catboost\n- Forecast multiple time series\n#### 02. [Backtest](https://github.com/tinkoff-ai/etna-ts/tree/master/examples/backtest.ipynb)\n- What is backtest and how it works\n- How to run a validation\n- Validation visualisation\n#### 03. [EDA](https://github.com/tinkoff-ai/etna-ts/tree/master/examples/EDA.ipynb) \n- Visualization\n    - Plot\n    - Partial autocorrelation\n    - Cross-correlation\n    - Distribution\n- Outliers\n     - Median method\n    - Density method\n\n## Documentation\nETNA documentation is available [here](https://etna-docs.netlify.app/).\n\n## Acknowledgments\n\n### ETNA.Team\n[Alekseev Andrey](https://github.com/iKintosh), \n[Shenshina Julia](https://github.com/julia-shenshina),\n[Gabdushev Martin](https://github.com/martins0n),\n[Kolesnikov Sergey](https://github.com/Scitator),\n[Bunin Dmitriy](https://github.com/Mr-Geekman),\n[Chikov Aleksandr](https://github.com/alex-hse-repository),\n[Barinov Nikita](https://github.com/diadorer),\n[Romantsov Nikolay](),\n[Makhin Artem](https://github.com/Ama16),\n[Denisov Vladislav](https://github.com/v-v-denisov),\n[Mitskovets Ivan](https://github.com/imitskovets),\n[Munirova Albina](https://github.com/albinamunirova)\n\n\n### ETNA.Contributors\n[Levashov Artem](https://github.com/soft1q),\n[Podkidyshev Aleksey](https://github.com/alekseyen)\n\n## License\n\nFeel free to use our library in your commercial and private applications.\n\nETNA is covered by [Apache 2.0](/LICENSE). \nRead more about this license [here](https://choosealicense.com/licenses/apache-2.0/)\n',
    'author': 'Andrey Alekseev',
    'author_email': 'an.alekseev@tinkoff.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tinkoff-ai/etna-ts',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<3.9.0',
}


setup(**setup_kwargs)
