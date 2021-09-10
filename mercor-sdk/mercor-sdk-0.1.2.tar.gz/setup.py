# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mercor_sdk', 'mercor_sdk.datatypes']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.11.1,<2.0.0',
 'eth-typing>=2.2.2,<3.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'mercor-sdk',
    'version': '0.1.2',
    'description': 'Software development kit for the Mercor trading API',
    'long_description': '# Mercor SDK\n\n## Introduction\n\nThe Mercor software development kit is meant for users of the Mercor trading\nAPI that wish to access it using the Python programming language. Using this\nSDK will have the benefit of removing some of the boilerplate for calling the\ndifferent endpoints.\n\n## Installation\n\n```\npython -m pip install mercor-sdk\n```\n\n## Usage\n\nImporting the client and token:\n\n``` python\nfrom mercor_sdk.client import MercorClient\nfrom mercor_sdk.tokens import CryptoToken\n```\n\nInstantiating the client:\n\n``` python\nclient = MercorClient("<my_algorithm_address>", "<my_password>")\n```\n\nViewing the current balance of the algorithm:\n\n``` python\nbalance = client.balance()\nprint(balance.supply)\n```\n\nPlacing a buy order:\n\n``` python\ntrade = client.buy(slippage=0.05, relative_amount=0.5)\nprint(trade.transaction_hash)\n```\n\nPlacing a sell order:\n\n``` python\ntrade = client.sell(slippage=0.05, relative_amount=0.5)\nprint(trade.transaction_hash)\n```\n\nRetrieving the status of a buy or sell order:\n\n``` python\nstatus = client.status(transaction_hash=trade.transaction_hash.value)\nprint(status.message)\n```\n\nAccessing data from the ticker:\n\n``` python\nticker = client.ticker_list()\nprint(ticker[CryptoToken.ETH])\n```\n\nAccessing data for a specific token from the ticker:\n\n``` python\ntoken = client.ticker(CryptoToken.ETH)\nprint(token.price)\n```\n',
    'author': 'Mercor Finance LLC',
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
