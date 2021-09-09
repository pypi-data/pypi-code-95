# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fcmeans']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.1,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['fcm = fcmeans.cli:app']}

setup_kwargs = {
    'name': 'fuzzy-c-means',
    'version': '1.6.2',
    'description': '',
    'long_description': '# fuzzy-c-means\n\n![GitHub](https://img.shields.io/github/license/omadson/fuzzy-c-means.svg)\n[![PyPI](https://img.shields.io/pypi/v/fuzzy-c-means.svg)](http://pypi.org/project/fuzzy-c-means/)\n[![GitHub commit activity](https://img.shields.io/github/commit-activity/w/omadson/fuzzy-c-means.svg)](https://github.com/omadson/fuzzy-c-means/pulse)\n[![GitHub last commit](https://img.shields.io/github/last-commit/omadson/fuzzy-c-means.svg)](https://github.com/omadson/fuzzy-c-means/commit/master)\n[![Downloads](https://pepy.tech/badge/fuzzy-c-means)](https://pepy.tech/project/fuzzy-c-means)\n[![DOI](https://zenodo.org/badge/186457481.svg)](https://zenodo.org/badge/latestdoi/186457481)\n\n\n`fuzzy-c-means` is a Python module implementing the [Fuzzy C-means][1] clustering algorithm.\n\n## installation\nthe `fuzzy-c-means` package is available in [PyPI](https://pypi.org/project/fuzzy-c-means/). to install, simply type the following command:\n```\npip install fuzzy-c-means\n```\n<!-- by default, the `fuzzy-c-means` uses [jax](https://github.com/google/jax) library, which only works on Linux systems. If you are a Windows user, try to install using:\n```\npip install fuzzy-c-means[windows]\n``` -->\n### command line interface\n<!-- if you prefer, you can install the command line interface so that you can use the library without having to program. To install, just use the command:\n```\npip install fuzzy-c-means[cli]\n``` -->\nYou can read the [CLI.md](https://github.com/omadson/fuzzy-c-means/blob/master/CLI.md) file for more information about this tool.\n\n<!-- ## running examples\n\nIf you want to run the examples on [examples/](https://github.com/omadson/fuzzy-c-means/tree/master/examples) folder, try to install the extra dependencies.\n\n```\npip install fuzzy-c-means[examples]\n``` -->\n\n### basic clustering example\nsimple example of use the `fuzzy-c-means` to cluster a dataset in two groups:\n\n#### importing libraries\n```Python\n%matplotlib inline\nimport numpy as np\nfrom fcmeans import FCM\nfrom matplotlib import pyplot as plt\n```\n\n#### creating artificial data set\n```Python\nn_samples = 3000\n\nX = np.concatenate((\n    np.random.normal((-2, -2), size=(n_samples, 2)),\n    np.random.normal((2, 2), size=(n_samples, 2))\n))\n```\n\n#### fitting the fuzzy-c-means\n```Python\nfcm = FCM(n_clusters=2)\nfcm.fit(X)\n```\n\n#### showing results\n```Python\n# outputs\nfcm_centers = fcm.centers\nfcm_labels = fcm.predict(X)\n\n# plot result\nf, axes = plt.subplots(1, 2, figsize=(11,5))\naxes[0].scatter(X[:,0], X[:,1], alpha=.1)\naxes[1].scatter(X[:,0], X[:,1], c=fcm_labels, alpha=.1)\naxes[1].scatter(fcm_centers[:,0], fcm_centers[:,1], marker="+", s=500, c=\'w\')\nplt.savefig(\'images/basic-clustering-output.jpg\')\nplt.show()\n```\n<div align="center">\n    <img src="https://raw.githubusercontent.com/omadson/fuzzy-c-means/master/examples/images/basic-clustering-output.jpg">\n</div>\n\nto more examples, see the [examples/](https://github.com/omadson/fuzzy-c-means/tree/master/examples) folder.\n\n\n## how to cite fuzzy-c-means package\nif you use `fuzzy-c-means` package in your paper, please cite it in your publication.\n```\n@software{dias2019fuzzy,\n  author       = {Madson Luiz Dantas Dias},\n  title        = {fuzzy-c-means: An implementation of Fuzzy $C$-means clustering algorithm.},\n  month        = may,\n  year         = 2019,\n  publisher    = {Zenodo},\n  doi          = {10.5281/zenodo.3066222},\n  url          = {https://git.io/fuzzy-c-means}\n}\n```\n\n### citations\n - [Gene-Based Clustering Algorithms: Comparison Between Denclue, Fuzzy-C, and BIRCH](https://doi.org/10.1177/1177932220909851)\n - [Analisis Data Log IDS Snort dengan Algoritma Clustering Fuzzy C-Means](https://doi.org/10.24843/MITE.2020.v19i01.P14)\n - [Comparative Analysis between the k-means and Fuzzy c-means Algorithms to Detect UDP Flood DDoS Attack on a SDN/NFV Environment](https://doi.org/10.5220/0010176201050112)\n - [Mixture-of-Experts Variational Autoencoder for Clustering and Generating from Similarity-Based Representations on Single Cell Data](https://arxiv.org/abs/1910.07763)\n - [Fuzzy Clustering: an Application to Distributional Reinforcement Learning](https://doi.org/10.34726/hss.2021.86783)\n\n\n## contributing and support\n\nthis project is open for contributions. here are some of the ways for you to contribute:\n - bug reports/fix\n - features requests\n - use-case demonstrations\n\nplease open an [issue](https://github.com/omadson/fuzzy-c-means/issues) with enough information for us to reproduce your problem. A [minimal, reproducible example](https://stackoverflow.com/help/minimal-reproducible-example) would be very helpful.\n\nto make a contribution, just fork this repository, push the changes in your fork, open up an issue, and make a pull request!\n\n## contributors\n - [Madson Dias](https://github.com/omadson)\n - [Dirk Nachbar](https://github.com/dirknbr)\n - [Alberth Florêncio](https://github.com/zealberth)\n\n[1]: https://doi.org/10.1016/0098-3004(84)90020-7\n[2]: http://scikit-learn.org/\n',
    'author': 'Madson Dias',
    'author_email': 'madsonddias@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/omadson/fuzzy-c-means',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
