# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tsflex',
 'tsflex.chunking',
 'tsflex.features',
 'tsflex.pipeline_sklearn_dev',
 'tsflex.processing',
 'tsflex.utils']

package_data = \
{'': ['*']}

install_requires = \
['dill>=0.3.3,<0.4.0',
 'fastparquet>=0.6.3,<0.7.0',
 'numpy>=1.19.0,<2.0.0',
 'pandas>=1.2.3,<2.0.0',
 'pathos>=0.2.7,<0.3.0',
 'tqdm>=4.60.0,<5.0.0']

setup_kwargs = {
    'name': 'tsflex',
    'version': '0.1.2.2',
    'description': 'Toolkit for flexible processing & feature extraction on time-series data',
    'long_description': '# <p align="center"> <a href="https://predict-idlab.github.io/tsflex"><img alt="tsflex" src="https://raw.githubusercontent.com/predict-idlab/tsflex/main/docs/_static/logo.png" height="100"></a></p>\n\n[![PyPI Latest Release](https://img.shields.io/pypi/v/tsflex.svg)](https://pypi.org/project/tsflex/)\n[![Conda Latest Release](https://img.shields.io/conda/vn/conda-forge/tsflex?label=conda)](https://anaconda.org/conda-forge/tsflex)\n[![support-version](https://img.shields.io/pypi/pyversions/tsflex)](https://img.shields.io/pypi/pyversions/tsflex)\n[![codecov](https://img.shields.io/codecov/c/github/predict-idlab/tsflex?logo=codecov)](https://codecov.io/gh/predict-idlab/tsflex)\n[![Code quality](https://img.shields.io/lgtm/grade/python/github/predict-idlab/tsflex?label=code%20quality&logo=lgtm)](https://lgtm.com/projects/g/predict-idlab/tsflex/context:python)\n![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?color=black)\n[![Downloads](https://pepy.tech/badge/tsflex)](https://pepy.tech/project/tsflex)\n[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?)](http://makeapullrequest.com) \n[![Documentation](https://github.com/predict-idlab/tsflex/actions/workflows/deploy-docs.yml/badge.svg)](https://github.com/predict-idlab/tsflex/actions/workflows/deploy-docs.yml)\n[![Testing](https://github.com/predict-idlab/tsflex/actions/workflows/test.yml/badge.svg)](https://github.com/predict-idlab/tsflex/actions/workflows/test.yml)\n\n<!-- ![Downloads](https://img.shields.io/conda/dn/conda-forge/tsflex?logo=anaconda) -->\n\n*tsflex* is a toolkit for _**flex**ible **t**ime **s**eries_ **[processing](https://predict-idlab.github.io/tsflex/processing) & [feature extraction](https://predict-idlab.github.io/tsflex/features)**, making few assumptions about input data. \n\n#### Useful links\n\n- [Documentation](https://predict-idlab.github.io/tsflex/)\n- [Example notebooks](https://github.com/predict-idlab/tsflex/tree/main/examples)\n\n## Installation\n\nIf you are using [**pip**](https://pypi.org/project/tsflex/), just execute the following command:\n\n```sh\npip install tsflex\n```\n\nOr, if you are using [**conda**](https://anaconda.org/conda-forge/tsflex), then execute this command:\n\n```sh\nconda install -c conda-forge tsflex\n```\n\n## Usage\n\n_tsflex_ is built to be intuitive, so we encourage you to copy-paste this code and toy with some parameters!\n\n### <a href="https://predict-idlab.github.io/tsflex/features/#getting-started">Feature extraction</a>\n\n```python\nimport pandas as pd; import numpy as np; import scipy.stats as ss\nfrom tsflex.features import MultipleFeatureDescriptors, FeatureCollection\n\n# 1. -------- Get your time-indexed data --------\nurl = "https://github.com/predict-idlab/tsflex/raw/main/examples/data/empatica/"\n# Contains 1 column; ["TMP"] - 4 Hz sampling rate\ndata_tmp = pd.read_parquet(url+"tmp.parquet").set_index("timestamp")\n# Contains 3 columns; ["ACC_x", "ACC_y", "ACC_z"] - 32 Hz sampling rate\ndata_acc = pd.read_parquet(url+"acc.parquet").set_index("timestamp")\n\n# 2. -------- Construct your feature collection --------\nfc = FeatureCollection(\n    MultipleFeatureDescriptors(\n          functions=[np.min, np.max, np.mean, np.std, np.median, ss.skew, ss.kurtosis],\n          series_names=["TMP", "ACC_x", "ACC_y"], # Use 3 multimodal signals \n          windows=["5min", "7.5min"],  # Use 5 minutes and 7.5 minutes \n          strides="2.5min",  # With steps of 2.5 minutes\n    )\n)\n\n# 3. -------- Calculate features --------\nfc.calculate(data=[data_tmp, data_acc])\n```\n\n### More examples\n\nFor processing [look here](https://predict-idlab.github.io/tsflex/processing/index.html#working-example)    \nOther examples can be found [here](https://github.com/predict-idlab/tsflex/tree/main/examples)\n\n## Why tsflex? ✨\n\n* flexible;\n    * handles multivariate/multimodal time series\n    * versatile function support  \n      => **integrates natively** with many packages for processing (e.g., [scipy.signal](https://docs.scipy.org/doc/scipy/reference/tutorial/signal.html), [statsmodels.tsa](https://www.statsmodels.org/stable/tsa.html#time-series-filters)) & feature extraction (e.g., [numpy](https://numpy.org/doc/stable/reference/routines.html), [scipy.stats](https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html), [seglearn](https://dmbee.github.io/seglearn/feature_functions.html)¹, [tsfresh](https://tsfresh.readthedocs.io/en/latest/text/list_of_features.html)¹, [tsfel](https://tsfel.readthedocs.io/en/latest/descriptions/feature_list.html)¹)\n    * feature-extraction handles **multiple strides & window sizes**\n* efficient view-based operations  \n  => extremely **low memory peak & fast execution times** ([see benchmarks](https://github.com/predict-idlab/tsflex-benchmarking))\n    <!-- * faster than any existing library (single- & multi-core)\n    * lower memory peak than any existing library (single- & multi-core) -->\n* maintains the **time-index** of the data\n* makes **little to no assumptions** about the time series data\n\n¹ These integrations are shown in [integration-example notebooks](https://github.com/predict-idlab/tsflex/tree/main/examples).\n\n## Future work 🔨\n\n* scikit-learn integration for both processing and feature extraction<br>\n  **note**: is actively developed upon [sklearn integration](https://github.com/predict-idlab/tsflex/tree/sklearn_integration) branch.\n* support for multi-indexed dataframes\n\n## Referencing our package\n\nIf you use `tsflex` in a scientific publication, we would highly appreciate citing us as:\n\n```bibtex\n@article{vanderdonckt2021tsflex,\n    author = {Van Der Donckt, Jonas and Van Der Donckt, Jeroen and Deprost, Emiel and Van Hoecke, Sofie},\n    title = {tsflex: flexible time series processing \\& feature extraction},\n    journal = {SoftwareX},\n    year = {2021},\n    url = {https://github.com/predict-idlab/tsflex},\n    publisher={Elsevier}\n}\n```\n\n---\n\n<p align="center">\n👤 <i>Jonas Van Der Donckt, Jeroen Van Der Donckt, Emiel Deprost</i>\n</p>\n',
    'author': 'Jonas Van Der Donckt, Jeroen Van Der Donckt, Emiel Deprost',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/predict-idlab/tsflex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
