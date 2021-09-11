# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tidycsv', 'tidycsv.core', 'tidycsv.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tidycsv',
    'version': '0.1.2',
    'description': 'A minimalistic solution to messy CSV files.',
    'long_description': '# tidyCSV.py\n\n[![CI build](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/main.yml/badge.svg)](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/main.yml)\n[![mypy](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/mypy.yml/badge.svg)](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/mypy.yml)\n[![tests](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/tests.yml/badge.svg)](https://github.com/gmagannaDevelop/tidyCSV.py/actions/workflows/tests.yml)\n[![codecov](https://codecov.io/gh/gmagannaDevelop/tidyCSV.py/branch/main/graph/badge.svg?token=H1H5RHHI9O)](https://codecov.io/gh/gmagannaDevelop/tidyCSV.py)\n![](https://enlyvfs9zh2z4g7.m.pipedream.net)\n\n![](https://img.shields.io/github/last-commit/gmagannaDevelop/tidyCSV.py)\n<a href="https://github.com/psf/black">\n\t<img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">\n</a>\n<a href="https://github.com/gmagannaDevelop/tidyCSV.py/blob/main/LICENSE">\n\t<img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg">\n</a>\n<a href="https://lifecycle.r-lib.org/articles/stages.html">\n\t<img alt="experimental" src="https://img.shields.io/badge/lifecycle-experimental-orange"> \n </a>\n\n<!-- Additions from black are the lincese and code style badges -->\n\nTired of having pseudo CSV files full of invalid entries ? Me too, this is my solution.\n\n\n\nIt has probably occurred to you as it has to me to get this error \nwhen reading a csv into Python using [pandas](https://pandas.pydata.org/).\n\n```python\nParserError: Error tokenizing data. C error: Expected 8 fields in line 7, saw 47\n```\n\nThis happens because some lines in your\nfile have more columns than you have\n in the header, or simply other kind of inconsistencies such as intermediate blank lines or lines containing random tokens.\n\nFear no more because _tidyCSV_ provides a simple and clear interface to access\nthe semantically coherent chunks of your csv file (if there are any). By default it selects the biggest group found (that is the one containing the most lines).\n\nMaybe I\'ll add an option to select how many columns you expect, in order to filter the groups according to a preconceived criteria. \nEventually I would like this project to become a command line tool as well as having a richer set of features, but It currently serves its purpose so it is not a priority.\n\n## Installation\n\nThe package has been published to PyPI! You can install it as any other package using **pip** (I recommend installing it \nwithin a virtual environment created in a per project basis).\n```bash\npip install tidycsv\n```\n\nOtherwise you can install the latest development version using:\n\n```bash\npip install git+https://github.com/gmagannaDevelop/tidyCSV.py\n```\n\n## Usage\n\nUse the context manager provided at top-level \nto read an otherwise unreadable csv as follows:\n\n```python\nimport pandas as pd\nfrom tidycsv import TidyCSV as tidycsv\n\nwith tidycsv("your-messy-csv-file.csv") as tidy:\n\tdf = pd.read_csv(tidy)\n\n```\n\nNow you have a dataframe ready to be used instead of an Exception.\n\n## Bugs and feature requests\n\nIf you find that _tidyCSV_ is not behaving as you would expect it to, please feel free to open an issue. The same goes for feature requests.\n',
    'author': 'Gustavo Magaña López',
    'author_email': 'gmaganna.biomed@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gmagannaDevelop/tidyCSV.py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
