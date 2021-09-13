# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['planetwatch']

package_data = \
{'': ['*']}

install_requires = \
['click', 'pycoingecko>=2.2.0,<3.0.0']

entry_points = \
{'console_scripts': ['planets = planetwatch.core:cli']}

setup_kwargs = {
    'name': 'planetwatch',
    'version': '0.1.2',
    'description': 'Code to make it easy to caluculate earnings, etc for planetwatch',
    'long_description': '# planetwatch\nCode to make it easier to figure out earnings and taxes for planetwatch\n\n\n## Install\nClone the repo, install python 3.7 or greater, and then install.\n\n```\ngit clone https://github.com/errantp/planetwatch.git\ncd planetwatch\npip install .\n\n```\n\n([poetry](https://python-poetry.org/) is also supported with `poetry install`)\n\n```\n❯ planets --help\nUsage: planets [OPTIONS]\n\nOptions:\n  --wallet TEXT    Planet Wallet  [required]\n  --currency TEXT  Currency to convert planets into.\n  --csv            Export csv of all transactions for given wallet\n  --help           Show this message and exit.\n```\n\n\n\n## Examples\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency eur\nThe current price in eur is : 0.166475\namount                310.976000\ncurrent_value_eur      51.769730\npurchase_value_eur     40.372615\ngain_eur               11.397115\ndtype: float64\n   amount        date  purchase_price_eur  current_value_eur  purchase_value_eur  gain_eur\n0  23.040  2021-09-10            0.159267           3.835584            3.669510  0.166074\n1  22.720  2021-09-09            0.152454           3.782312            3.463757  0.318555\n2  23.040  2021-09-08            0.149045           3.835584            3.433999  0.401585\n3  23.040  2021-09-07            0.146756           3.835584            3.381269  0.454315\n4  23.040  2021-09-06            0.135407           3.835584            3.119766  0.715818\n5  23.040  2021-09-05            0.126531           3.835584            2.915269  0.920315\n6  23.040  2021-09-04            0.123744           3.835584            2.851070  0.984514\n7  20.512  2021-09-03            0.121153           3.414735            2.485092  0.929643\n8  15.936  2021-09-02            0.120051           2.652946            1.913135  0.739810\n9   3.360  2021-09-01            0.119421           0.559356            0.401253  0.158103\n```\n\n\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency usd\nThe current price in usd is : 0.196685\namount                310.976000\ncurrent_value_usd      61.164315\npurchase_value_usd     47.790114\ngain_usd               13.374201\ndtype: float64\n   amount        date  purchase_price_usd  current_value_usd  purchase_value_usd  gain_usd\n0  23.040  2021-09-10            0.188485           4.531622            4.342697  0.188925\n1  22.720  2021-09-09            0.180454           4.468683            4.099926  0.368757\n2  23.040  2021-09-08            0.176202           4.531622            4.059700  0.471923\n3  23.040  2021-09-07            0.174077           4.531622            4.010729  0.520894\n4  23.040  2021-09-06            0.160621           4.531622            3.700707  0.830915\n5  23.040  2021-09-05            0.150363           4.531622            3.464360  1.067263\n6  23.040  2021-09-04            0.147052           4.531622            3.388068  1.143554\n7  20.512  2021-09-03            0.143852           4.034403            2.950683  1.083720\n8  15.936  2021-09-02            0.142276           3.134372            2.267304  0.867068\n9   3.360  2021-09-01            0.141103           0.660862            0.474107  0.186755\n```\n\n\n### Export as CSV\n\n```\n❯ planets --wallet GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY --currency usd --csv\n```\nWill generate the same output expect it will also create a file called `GYLEOJFHACSCATPBVQ345UCMCOMSGV76X4XTVOLHGXKOCJL44YBUAHXJOY.csv`\n',
    'author': 'errantp',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
