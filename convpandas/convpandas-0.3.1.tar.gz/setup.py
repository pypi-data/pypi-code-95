# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['convpandas', 'convpandas.command', 'convpandas.common']

package_data = \
{'': ['*']}

install_requires = \
['openpyxl', 'pandas>=1.2,<2.0']

entry_points = \
{'console_scripts': ['convpandas = convpandas.__main__:cli']}

setup_kwargs = {
    'name': 'convpandas',
    'version': '0.3.1',
    'description': 'Convert file format with pandas',
    'long_description': '# convert-fileformat-with-pandas\nConvert file format with [pandas](https://pandas.pydata.org/).\n\n[![Build Status](https://travis-ci.org/yuji38kwmt/convpandas.svg?branch=master)](https://travis-ci.org/yuji38kwmt/convpandas)\n[![PyPI version](https://badge.fury.io/py/convpandas.svg)](https://badge.fury.io/py/convpandas)\n[![Python Versions](https://img.shields.io/pypi/pyversions/convpandas.svg)](https://pypi.org/project/convpandas/)\n\n# Requirements\n* Python 3.7+\n\n# Install\n\n```\n$ pip install convpandas\n```\n\nhttps://pypi.org/project/convpandas/\n\n\n# Usage\n\n## csv2xlsx\nConvert csv file to xlsx file.\n\n```\n$ convpandas csv2xlsx --help\nusage: convpandas csv2xlsx [-h] [--sep SEP] [--encoding ENCODING] [--quotechar QUOTECHAR] [--numeric_to_string] [--sheet_name SHEET_NAME [SHEET_NAME ...]]\n                           csv_files [csv_files ...] xlsx_file\n\npositional arguments:\n  csv_files\n\n  xlsx_file\n\noptional arguments:\n  -h, --help            show this help message and exit\n\n  --sep SEP             Delimiter to use when reading csv. (default: ,)\n\n  --encoding ENCODING   Encoding to use when reading csv. List of Python standard encodings.\n                        https://docs.python.org/3/library/codecs.html#standard-encodings (default: utf-8)\n\n  --quotechar QUOTECHAR\n                        The character used to denote the start and end of a quoted item when reading csv. (default: ")\n\n  --numeric_to_string   If specified, write numeric value as string type. If not specified, write numeric value as numeric type. (default: False)\n\n  --sheet_name SHEET_NAME [SHEET_NAME ...]\n```\n\n\nConvert `in.csv` to `out.xlsx` .\n\n```\n$ convpandas csv2xlsx in.csv out.xlsx\n```\n\n\nWhen `CSV_FILE` is `-` , STDIN is used for input. \n\n```\n$ convpandas csv2xlsx - out.xlsx < in.csv\n```\n\nConvert `in1.csv` and `in2.csv` to `out.xlsx` . Sheet name is csv filename without its\' suffix.  \n\n```\n$ convpandas csv2xlsx in1.csv in2.csv out.xlsx\n```\n\n![](docs/img/output_xlsx_file_from_multiple_csv.png)\n\nIf `--sheet_name` is specified, sheet name is set.\n\n```\n$ convpandas csv2xlsx in1.csv in2.csv out.xlsx --sheet_name foo bar\n```\n\n![](docs/img/output_xlsx_file_from_multiple_csv2.png)\n\n## xlsx2csv\nConvert xlsx file to csv file.\n\n```\n$ convpandas xlsx2csv --help\nusage: convpandas xlsx2csv [-h] [--sheet_name SHEET_NAME] [--sep SEP] [--encoding ENCODING] [--quotechar QUOTECHAR] xlsx_file csv_file\n\npositional arguments:\n  xlsx_file\n\n  csv_file\n\noptional arguments:\n  -h, --help            show this help message and exit\n\n  --sheet_name SHEET_NAME\n                        Sheet name when reading xlsx. If not specified, read 1st sheet. (default: None)\n\n  --sep SEP             Field delimiter for the output file. (default: ,)\n\n  --encoding ENCODING   A string representing the encoding to use in the output file. (default: utf-8)\n\n  --quotechar QUOTECHAR\n                        Character used to quote fields. (default: ")\n```\n\n\nConvert `in.xlsx` to `out.csv` .\n\n```\n$ convpandas csv2xlsx in.xlsx out.csv\n```\n\n\nWhen `CSV_FILE` is `-` , write to STDOUT. \n\n```\n$ convpandas csv2xlsx in.xlsx -\nname,age\nAlice,23\n```\n\nWith specifying `--sheet_name`, you can select sheet name that you want to convert.\n\n```\n$ convpandas csv2xlsx in.xlsx out.csv --sheet_name sheet2\n```\n',
    'author': 'yuji38kwmt',
    'author_email': None,
    'maintainer': 'yuji38kwmt',
    'maintainer_email': None,
    'url': 'https://github.com/yuji38kwmt/convert-fileformat-with-pandas.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
