# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bayex']

package_data = \
{'': ['*']}

install_requires = \
['jax>=0.2.18,<0.3.0', 'jaxlib>=0.1.69,<0.2.0']

setup_kwargs = {
    'name': 'bayex',
    'version': '0.1.0a0',
    'description': 'Bayesian Optimization with Gaussian Processes powered by JAX',
    'long_description': "# BAYEX: Bayesian Optimization powered by JAX\nBayex is a Bayesian global optimization library using Gaussian processes.\nIn contrast to existing Bayesian optimization libraries, Bayex is designed for JAX.\n\nInstead of relaying on external libraries, Bayex only relies on JAX and its custom implementations, without requiring importing massive libraries such as `sklearn`.\n\n## What is Bayesian Optimization?\n\nBayesian Optimization (BO) methods are useful for optimizing functions that are expensive to evaluate, lack an analytical expression and whose evaluations can be contaminated by noise. These methods rely on a probabilistic model of the objective function, typically a Gaussian process (GP), upon which an acquisition function is built. The acquisition function guides the optimization process and measures the expected utility of performing an evaluation of the objective at a new point. \n\n## Why JAX?\nUsing JAX as a backend removes some of the limitations found on Python, as it gives us direct mapping to the XLA compiler.\n\nXLA compiles and runs the JAX code into several architectures such as CPU, GPU and TPU without hassle. But the device agnostic approach is not the reason to back XLA for future scientific programs. XLA provides with optimizations under the hood such as Just-In-Time compilation and automatic parallelization that make Python (with a NumPy-like approach) a suitable candidate on some High Performance Computing scenarios.\n\nAdditionally, JAX provides Python code with automatic differentiation, which helps identify the conditions that maximize the acquisition function.\n\n\n## Installation\nBayex can be installed using PyPI via `pip`:\n```\npip install bayex\n```\nor from GitHub directly\n```\npip install git+git://github.com/alonfnt/bayex.git\n```\n## Getting Started\n```python\nimport bayex\n\ndef f(x, y):\n    return -y ** 2 - (x - y) ** 2 + 3 * x / y - 2\n\nconstrains = {'x': (-10, 10), 'y': (0, 10)}\nx_max, y_max = bayex.optim(f, constrains=constrains, seed=42)\n```\n\n## Contributing\nEveryone can contribute to Bayex and we welcome pull requests as well as raised issues.\nIn order to contribute code, one must begin by forking the repository. This creates a copy of the repository on your account.\n\nBayex uses poetry as a packaging and dependency manager. Hence, once you have cloned your repo on your own machine, you can use\n```\npoetry install\n```\nto install on the dependencies needed.\nYou should start a new branch to write your changes on\n```\ngit checkout -b name-of-change\n``` \nor \n```\ngit branch name-of-change\ngit checkout name-of-change\n```\n\nIt is welcome if PR are composed of a single commit, to keep the feature <-> commit balance.\nPlease, when writing the commit message, follow the [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) specitifcation.\nOnce you have made your changes and created your commit. It is recommended to run the pre-commit checks.\n```\npre-commit run --all\n```\nas well as the tests to make sure everything works\n```\npytest -n auto tests/\n```\n\nRemember to amend your current commit with the fixes if any of the checks fails.\n\n## Planned Features\n- [ ] Optimization on continuos domains.\n- [ ] Integer parameters support.\n- [ ] Categorical Variables \n- [ ] Automatic Parallelization on XLA Devices.\n\n## Citation\nTo cite this repository\n```\n@software{\n  author = {Albert Alonso, Jacob Ungar Felding},\n  title = {{Bayex}: Bayesian Global Optimization with JAX tool for {P}ython+{N}um{P}y programs},\n  url = {http://github.com/alonfnt/bayex},\n  version = {0.0.0},\n  year = {2021},\n}\n```\n## References\n1. [A Tutorial on Bayesian Optimization](https://arxiv.org/abs/1807.02811)\n2. [BayesianOtpimization Library](https://github.com/fmfn/BayesianOptimization)\n3. [JAX: Autograd and XLA](https://github.com/google/jax)\n",
    'author': 'Albert Alonso',
    'author_email': 'alonfnt@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alonfnt/bayex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
