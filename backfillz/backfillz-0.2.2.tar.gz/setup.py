# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['backfillz', 'backfillz.example']

package_data = \
{'': ['*']}

install_requires = \
['importlib_metadata==3.4.0',
 'kaleido==0.2.1',
 'nbval>=0.9.6,<0.10.0',
 'numpy==1.20.3',
 'plotly>=4.14.3,<5.0.0',
 'pystan==3.0.0',
 'scipy>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'backfillz',
    'version': '0.2.2',
    'description': 'MCMC visualisations package developed at the University of Warwick and supported by The Alan Turing Institute.',
    'long_description': '<!-- badges: start -->\n\n[![Release build](https://github.com/WarwickCIM/backfillz-py/actions/workflows/build-publish.yml/badge.svg?branch=release)](https://github.com/WarwickCIM/backfillz-py/actions/workflows/build-publish.yml)\n[![Develop build](https://github.com/WarwickCIM/backfillz-py/actions/workflows/build-publish.yml/badge.svg?branch=develop)](https://github.com/WarwickCIM/backfillz-py/actions/workflows/build-publish.yml)\n[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#active)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n<!-- badges: end -->\n\n<img src="https://github.com/WarwickCIM/backfillz/raw/master/fig1.png" width=100% alt=""/>\n\n# New View of MCMC\n\nBackfillz-py provides new visual diagnostics for understanding MCMC (Markov Chain Monte Carlo) analyses and outputs. MCMC chains can defy a simple line graph. Unless the chain is very short (which isn’t often the case), plotting tens or hundreds of thousands of data points reveals very little other than a ‘trace plot’ where we only see the outermost points. Common plotting methods may only reveal when an MCMC really hasn’t worked, but not when it has.\nBackFillz-py slices and dices MCMC chains so increasingly parameter rich, complex analyses can be visualised meaningfully. What does ‘good mixing’ look like? Is a ‘hair caterpillar’ test verifiable? What does a density plot show and what does it hide?\n\n# Quick Start\n\nInstall from [PyPI](https://pypi.org/project/backfillz/) using `pip install backfillz`.\n\n```python\nfrom backfillz import Backfillz\n\n# Let\'s have an example Stan model.\nfrom backfillz.example.eight_schools import generate_fit\n\nbackfillz = Backfillz(generate_fit().fit)\n\n# Plot some of the available plot types.\nbackfillz.plot_slice_histogram(\'mu\')\nbackfillz.plot_trace_dial(\'theta\')\nbackfillz.plot_spiral_stream(\'mu\', [2, 8, 15, 65, 250, 600])\n```\n\nSee the [example notebook](https://github.com/WarwickCIM/backfillz-py/blob/develop/notebooks/example.ipynb) for running in JupyterLab.\n\n# Current supported plot types\n\n## Pretzel Plot – plot_trace_dial()\n\nThis plot shows the chain and summary histograms in a format that can be easily arranged as a grid. The trace plot is stretched, clearly indicating ‘burn-in’, with density plots showing the burn-in and remainder of the chain in context.\n\n<img src="tests/expected_trace_dial.png" width=100% alt=""/>\n\n## Slice plot - plot_slice_histogram()\n\nBy partitioning chain slices, in a faceted view, users can assess chain convergence. The slices are currently specified by the user and display density plots for each slice. Have my chains converged? The slice plot offers a clear view of when and how convergence is achieved. Further statistical diagnostics can be embedded in these plots as colour encodings or additional layers and annotations.\n\n<img src="tests/expected_slice_histogram.png" width=100% alt=""/>\n\n## Splash plot - plot_spiral_stream()\n\nBased on a Theodorus spiral, we turn MCMC chains into glyphs and extract properties to answer – What does ‘good mixing’ look like? In these plots variance windows are calculated across chains and parameters. The glyphs have clear diagnostic features and will allow gridded plots to investigate large numbers of parameters.\n\n<img src="tests/expected_spiral_stream.png" width=100% alt=""/>\n\n# Emojis on commit messages\n\nRecent commits use the following `git` aliases (add to `[alias]` section of your `.gitconfig`):\n\n```\ndoc      = "!f() { git commit -a -m \\"📚 : $1\\"; }; f"\nlint     = "!f() { git commit -a -m \\"✨ : $1\\"; }; f"\nmodify   = "!f() { git commit -a -m \\"❗ : $1\\"; }; f"\nrefactor = "!f() { git commit -a -m \\"♻️ : $1\\"; }; f"\n```\n\n# Acknowledgements\n\nWe are grateful for funding from the Alan Turing Institute within the [Tools, Practices and Systems](https://www.turing.ac.uk/research/research-programmes/tools-practices-and-systems) theme. Initial user research was carried out by GJM on the [2020 Science programme](www.2020science.net/) funded by the EPSRC Cross-Discipline Interface Programme (grant number EP/I017909/1).\n',
    'author': 'James Tripp',
    'author_email': 'james.tripp@warwick.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/WarwickCIM/backfillz-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.0,<3.10',
}


setup(**setup_kwargs)
