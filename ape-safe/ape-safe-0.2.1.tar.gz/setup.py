# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ape_safe']
install_requires = \
['eth-brownie>=1.16.3,<2.0.0', 'gnosis-py>=3.2.2,<4.0.0']

setup_kwargs = {
    'name': 'ape-safe',
    'version': '0.2.1',
    'description': 'Build complex Gnosis Safe transactions and safely preview them in a forked environment.',
    'long_description': "# Ape Safe: Gnosis Safe tx builder\n\nApe Safe allows you to iteratively build complex multi-step Gnosis Safe transactions and safely preview their side effects from the convenience of a locally forked mainnet environment.\n\n## Installation\n\n```\npip install -U ape-safe\n```\n\n## Quickstart\n\n```bash\nbrownie console --network mainnet-fork\n```\n\n```python\nfrom ape_safe import ApeSafe\nsafe = ApeSafe('ychad.eth')\n\ndai = safe.contract('0x6B175474E89094C44Da98b954EedeAC495271d0F')\nvault = safe.contract('0x19D3364A399d251E894aC732651be8B0E4e85001')\n\namount = dai.balanceOf(safe.account)\ndai.approve(vault, amount)\nvault.deposit(amount)\n\nsafe_tx = safe.multisend_from_receipts()\nsafe.preview(safe_tx)\nsafe.post_transaction(safe_tx)\n```\n\nSee [Documentation](https://safe.ape.tax/) for more examples and full reference.\n",
    'author': 'banteg',
    'author_email': 'banteeg@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/banteg/ape-safe',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
