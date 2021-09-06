# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pydrift', 'pydrift.test']

package_data = \
{'': ['*'], 'pydrift': ['core/*']}

install_requires = \
['catboost>=0.23,<0.24',
 'pandas>=1.0.3,<2.0.0',
 'scikit-learn>=0.23.1,<0.24.0',
 'shap>=0.35.0,<0.36.0',
 'statsmodels>=0.11.1,<0.12.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.7.4,<4.0.0'],
 'plotting': ['plotly>=4.8.1,<5.0.0']}

setup_kwargs = {
    'name': 'pydrift',
    'version': '0.2.14',
    'description': 'How do we measure the degradation of a machine learning process? Why does the performance of our predictive models decrease? Maybe it is that a data source has changed (one or more variables) or maybe what changes is the relationship of these variables with the target we want to predict. `pydrift` tries to facilitate this task to the data scientist, performing this kind of checks and somehow measuring that degradation.',
    'long_description': '# Welcome to `pydrift` 0.2.14\n\nHow do we measure the degradation of a machine learning process? Why does the performance of our predictive models decrease? Maybe it is that a data source has changed (one or more variables) or maybe what changes is the relationship of these variables with the target we want to predict. `pydrift` tries to facilitate this task to the data scientist, performing this kind of checks and somehow measuring that degradation.\n\n# Install `pydrift`\n\nWith **pip**:\n\n`pip install pydrift`\n\nWith **conda**:\n\n`conda install -c conda-forge pydrift`\n\nWith **poetry**\n\n`poetry add pydrift`\n\n# Structure\n\nThis is intended to be user-friendly. pydrift is divided into **DataDriftChecker** and **ModelDriftChecker**:\n\n- **DataDriftChecker**: searches for drift in the variables, check if their distributions have changed\n- **ModelDriftChecker**: searches for drift in the relationship of the variables with the target, checks that the model behaves the same way for both data sets\n\nBoth can use a discriminative model (defined by parent class **DriftChecker**), where the target would be binary in belonging to one of the two sets, 1 if it is the left one and 0 on the contrary. If the model is not able to differentiate given the two sets, there is no difference!\n\n![Class inheritance](https://raw.githubusercontent.com/sergiocalde94/pydrift/master/images/class_inheritance.png)\n\nIt also exists `InterpretableDrift` and `DriftCheckerEstimator`:\n \n- **InterpretableDrift**: manages all of the stuff related to interpretability of drifting. It can show us the features distribution or the most important features when we are training a discriminative model or our predictive one\n- **DriftCheckerEstimator**: allows `pydrift` to be used as a sklearn estimator, it works lonely or in a pipeline, like any sklearn estimator\n\n# Usage\n\nYou can take a look to the `notebooks` folder where you can find one example for generic `DriftChecker`, one for `DataDriftChecker` and other one for `ModelDriftChecker`. \n\n# Correct Notebooks Render\n\nBecause `pydrift` uses plotly and GitHub performs a static render of the notebooks figures do not show correctly. For a rich view of the notebook, you can visit  [nbviewer](http://nbviewer.jupyter.org/) and paste the link to the notebook you want to show, for example if you want to render **1-Titanic-Drift-Demo.ipynb** you have to paste https://github.com/sergiocalde94/pydrift/blob/master/notebooks/1-Titanic-Drift-Demo.ipynb into nbviewer.  \n\n# More Info\n\nFor more info check the docs available [here](https://sergiocalde94.github.io/pydrift/)\n\nMore demos and code improvements will coming, **if you want to contribute you can contact me (sergiocalde94@gmail.com)**, in the future I will upload a file to explain how this would work.\n',
    'author': 'sergiocalde94',
    'author_email': 'sergiocalde94@gmail.com',
    'url': 'https://github.com/sergiocalde94/pydrift',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
