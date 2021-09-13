# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_prophet',
 'streamlit_prophet.app',
 'streamlit_prophet.cli',
 'streamlit_prophet.lib',
 'streamlit_prophet.lib.dataprep',
 'streamlit_prophet.lib.evaluation',
 'streamlit_prophet.lib.exposition',
 'streamlit_prophet.lib.inputs',
 'streamlit_prophet.lib.models',
 'streamlit_prophet.lib.utils']

package_data = \
{'': ['*'],
 'streamlit_prophet': ['config/config_instructions.toml',
                       'config/config_instructions.toml',
                       'config/config_instructions.toml',
                       'config/config_readme.toml',
                       'config/config_readme.toml',
                       'config/config_readme.toml',
                       'config/config_streamlit.toml',
                       'config/config_streamlit.toml',
                       'config/config_streamlit.toml',
                       'references/input_format.png',
                       'references/input_format.png',
                       'references/logo.png',
                       'references/logo.png',
                       'report/config/.gitignore',
                       'report/data/.gitignore',
                       'report/plots/.gitignore']}

install_requires = \
['fbprophet==0.7.1',
 'holidays>=0.11.1,<0.12.0',
 'numpy>=1.20.2,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'plotly>=4.11.0,<5.0.0',
 'pystan==2.19.1.1',
 'rich>=10.1.0,<11.0.0',
 'scipy>=1.6.3,<2.0.0',
 'streamlit==0.80.0',
 'typer[all]>=0.3.2,<0.4.0',
 'vacances-scolaires-france>=0.8.0,<0.9.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=1.6.0,<2.0.0']}

entry_points = \
{'console_scripts': ['streamlit_prophet = streamlit_prophet.cli.__main__:app']}

setup_kwargs = {
    'name': 'streamlit-prophet',
    'version': '1.0.0',
    'description': 'Deploy a Streamlit app to train, evaluate and optimize a Prophet forecasting model visually.',
    'long_description': '<div align="center">\n\n![](streamlit_prophet/references/logo.png)\n\n[![CI status](https://github.com/artefactory-global/streamlit_prophet/actions/workflows/ci.yml/badge.svg?branch%3Amain&event%3Apush)](https://github.com/artefactory-global/streamlit_prophet/actions/workflows/ci.yml?query=branch%3Amain)\n[![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)](#supported-python-versions)\n[![Dependencies Status](https://img.shields.io/badge/dependabots-active-informational.svg)](https://github.com/artefactory-global/streamlit_prophet/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-informational.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-informational?logo=pre-commit&logoColor=white)](https://github.com/artefactory-global/streamlit_prophet/blob/main/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%F0%9F%9A%80-semantic%20versions-informational.svg)](https://github.com/artefactory-global/streamlit_prophet/releases)\n[![License](https://img.shields.io/badge/License-MIT-informational.svg)](https://github.com/artefactory-global/streamlit_prophet/blob/main/LICENSE)\n\nDeploy a [Streamlit](https://streamlit.io/) app to train, evaluate and optimize a [Prophet](https://facebook.github.io/prophet/) forecasting model visually\n\n</div>\n\nhttps://user-images.githubusercontent.com/56996548/126762714-f2d3f3a1-7098-4a86-8c60-0a69d0f913a7.mp4\n\n## 💻 Requirements\n\n### Python version\n* Main supported version : <strong>3.7</strong> <br>\n* Other supported versions : <strong>3.8</strong> & <strong>3.9</strong>\n\nPlease make sure you have one of these versions installed to be able to run the app on your machine.\n\n### Operating System\nWindows users have to install [WSL2](https://docs.microsoft.com/en-us/windows/wsl/) to download the package. \nThis is due to an incompatibility between Windows and Prophet\'s main dependency (pystan). \nOther operating systems should work fine.\n\n## ⚙️ Installation\n\n\n### Create a virtual environment (optional)\nWe strongly advise to create and activate a new virtual environment, to avoid any dependency issue.\n\nFor example with conda:\n```bash\npip install conda; conda create -n streamlit_prophet python=3.7; conda activate streamlit_prophet\n```\n\nOr with virtualenv:\n```bash\npip install virtualenv; python3.7 -m virtualenv streamlit_prophet --python=python3.7; source streamlit_prophet/bin/activate\n```\n\n\n### Install package\nInstall the package from PyPi (it should take a few minutes):\n```bash\npip install -U streamlit_prophet\n```\n\nOr from the main branch of this repository:\n```bash\npip install git+https://github.com/artefactory-global/streamlit_prophet.git@main\n```\n\n\n## 📈 Usage\n\nOnce installed, run the following command from CLI to open the app in your default web browser:\n\n```bash\nstreamlit_prophet deploy dashboard\n```\n\nNow you can train, evaluate and optimize forecasting models in a few clicks.\nAll you have to do is to upload a time series dataset. \nThis dataset should be a csv file that contains a date column, a target column and optionally some features, like on the example below:\n\n![](streamlit_prophet/references/input_format.png)\n\nThen, follow the guidelines in the sidebar to:\n\n* <strong>Prepare data</strong>: Filter, aggregate, resample and/or clean your dataset.\n* <strong>Choose model parameters</strong>: Default parameters are available but you can tune them.\nLook at the tooltips to understand how each parameter is impacting forecasts.\n* <strong>Select evaluation method</strong>: Define the evaluation process, the metrics and the granularity to\nassess your model performance.\n* <strong>Make a forecast</strong>: Make a forecast on future dates that are not included in your dataset,\nwith the model previously trained.\n\nOnce you are satisfied, click on "save experiment" to download all plots and data locally.\n\n\n## 🛠️ How to contribute ?\n\nAll contributions, ideas and bug reports are welcome! \nWe encourage you to open an [issue](https://github.com/artefactory-global/streamlit_prophet/issues) for any change you would like to make on this project.\n\n\nFor more information, see [`CONTRIBUTING`](https://github.com/artefactory-global/streamlit_prophet/blob/main/CONTRIBUTING.md) instructions.\nIf you wish to containerize the app, see [`DOCKER`](https://github.com/artefactory-global/streamlit_prophet/blob/main/DOCKER.md) instructions.\n',
    'author': 'Maxime Lutel',
    'author_email': 'maxime.lutel@artefact.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/artefactory-global/streamlit_prophet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
