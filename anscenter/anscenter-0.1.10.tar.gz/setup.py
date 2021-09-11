# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anscenter',
 'anscenter.app',
 'anscenter.app.api',
 'anscenter.app.api.routes',
 'anscenter.app.core',
 'anscenter.app.model',
 'anscenter.app.services']

package_data = \
{'': ['*'], 'anscenter': ['ml/libs/*', 'ml/model/*']}

install_requires = \
['fastapi[testclient]>=0.68.1,<0.69.0',
 'joblib>=1.0.1,<2.0.0',
 'loguru>=0.4.0,<0.5.0',
 'pydantic>=1.3,<2.0',
 'pytest>=6.2.4,<7.0.0',
 'requests>=2.22.0,<3.0.0',
 'uvicorn>=0.11.1,<0.12.0']

setup_kwargs = {
    'name': 'anscenter',
    'version': '0.1.10',
    'description': 'Backend module for ANSCENTER project',
    'long_description': '# backend-module\n\nMain backend module, which is used for developing web-app logic and deploying AI model.\n\n## Installation\nRun the following to install:\n```python\npip install anscenter\n```\n\n## Usage\n```python\nfrom anscester.predict import MachineLearningModel\n\n# Generate model\nmodel = MachineLearningModel()\n\n# Using Example\ndata_input = [1.0, 2.0, 3.0, 4.0]\nresult = model.predict(data_input)\nprint(result)\n```\n\n## Developing HelloG\nTo install helloG, along with the tools you need to develop and run tests, run the following in your virtualenv:\n```bash\n$ pip install anscenter[dev]\n```',
    'author': 'ARI Technology',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
