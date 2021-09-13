# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tabular_time_series']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.2,<2.0.0', 'pre-commit>=2.15.0,<3.0.0']

setup_kwargs = {
    'name': 'tabular-time-series',
    'version': '1.1.3',
    'description': '',
    'long_description': "# Tabular Time Series\n\n## Summary\n\nThis repo was created as I did not find a function able to transform a time-series (1D) into a tabular format (X, y).\n\n## Usage\n\n### TimeSeriesGenerator\n\nThe docstring is as follows. Given a 1D array `data = [0, 1, 2, 3, 4, 5, 6]`, generates `X, y` following the parameters `p`(autoregressive), `s` (seasonal) and `n` (lenght of y).\n\nTherefore, it makes it possible to train a neural network (e.g.) that 2 autoregressive entries (e.g. `p = 2`) and predicts the next two (`n = 2`) using 2 (`n = 2`) entries with lag 4 (`s = 4`).\n\n```python\n>> data = [0, 1, 2, 3, 4, 5, 6]\n>> p, n = 2, 2\n>> ts = TimeSeriesGenerator(data, p, n)\n>> for _, X, y in ts:\n...    print(X, y)\n    [0, 1] [2, 3]\n    [1, 2] [3, 4]\n    [2, 3] [4, 5]\n    [3, 4] [5, 6]\n>> p, n, s = 2, 2, 4\n>> ts = TimeSeriesGenerator(data, p, n, s)\n>> for X, y in ts:\n...    # both y have their respective seasonal entry\n...    print(data.index(y[0]) - data.index(X[0]) == s, data.index(y[1]) - data.index(X[1]) == s)\n...    print(X, y)\n    [0, 1], [2, 3] [4, 5]\n    [1, 2], [3, 4] [5, 6]\n```\n\n### TimeSeriesGeneratorOnline\n\nTo support online learning (and streaming) applications, `TimeSeriesGeneratorOnline` enables applications to give real time measurements and returns a bool `b` stating if it was possible to generate features, considering the given seasonal `s`, autoregressive `ar` and output `y`.\n\n```python\n>>> from tabular_time_series.tsgeneratoronline import TimeSeriesGeneratorOnline\n>>> data = [i for i in range(10)]\n>>> p, n, s = 2, 2, 4\n>>> tsgo = TimeSeriesGeneratorOnline(p, n, s)\n>>> for X in data:\n...     b, (s, ar, y) = tsgo(X)\n...     print(X, '|', b, s, ar, y)\n...\n0 | False None None None\n1 | False None None None\n2 | False None None None\n3 | False None None None\n4 | False None None None\n5 | False None None None\n6 | True [0, 1] [2, 3] [4, 5]\n7 | True [1, 2] [3, 4] [5, 6]\n8 | True [2, 3] [4, 5] [6, 7]\n9 | True [3, 4] [5, 6] [7, 8]\n```\n\n### timeseries2df\n\nConsidering that many times a batch array is needed for training, `timeseries2df` can be used to generate a `pandas` DataFrame that will contain columns in the format:\n\n```python\n>>> from tabular_time_series.tsdf import timeseries2df\n>>> data = list(range(10))\n>>> p, n, s = 2, 2, 4\n>>> df = timeseries2df(data, p, n, s)\n>>> df\n   y(ts4)_1  y(ts4)_2  y(t-1)  y(t-0)  y(t+1)  y(t+2)\n0         0         1       2       3       4       5\n1         1         2       3       4       5       6\n2         2         3       4       5       6       7\n3         3         4       5       6       7       8\n4         4         5       6       7       8       9\n```\n",
    'author': 'Felipe Whitaker',
    'author_email': 'felipewhitaker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/felipewhitaker/tabular-time-series',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
