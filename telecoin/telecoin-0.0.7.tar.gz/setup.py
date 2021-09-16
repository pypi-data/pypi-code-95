# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['telecoin']

package_data = \
{'': ['*']}

install_requires = \
['Pyrogram==1.2.9', 'aiohttp==3.7.4.post0']

setup_kwargs = {
    'name': 'telecoin',
    'version': '0.0.7',
    'description': 'Simple library to make payments via telegram bitcoin exchangers',
    'long_description': "### 💾 Installation\n\n```bash\npip install telecoin\n```\n\n---\n\n## 📞 Contacts\n* 🖱️ __Developer contacts: [![Dev-Telegram](https://img.shields.io/badge/Telegram-blue.svg?style=flat-square&logo=telegram)](https://t.me/marple_tech)__\n\n---\n\n## 🐦 Dependencies  \n\n| Library | Description                                            |\n|:-------:|:----------------------------------------------:        |\n|aiohttp  | Asynchronous HTTP Client/Server for asyncio and Python.|\n|pyrogram | Modern Telegram Framework                             |\n\n---\n\n## ↗️ Create Session\n```python\nimport asyncio\n\nfrom telecoin import BankerWrapper\n\n\nasync def main():\n    banker = BankerWrapper(phone_number='Your Number', api_id='Your ID',\n                           api_hash='Your Hash',\n                           session_name='i_love_telecoin')\n    await banker.create_session()\n\n\nif __name__ == '__main__':\n    asyncio.run(main())\n```\n\n---\n\n## 💰 Activate Cheque\n```python\nimport asyncio\n\nimport telecoin.exceptions\nfrom telecoin import BankerWrapper\n\n\nasync def main():\n    banker = BankerWrapper(phone_number='Your Number', api_id='Your ID',\n                           api_hash='Your Hash',\n                           session_name='i_love_telecoin')\n    await banker.create_session()\n    result = await banker.activate_cheque(cheque='https://telegram.me/BTC_CHANGE_BOT?start=c_59500d20eaac0ac2b479382409596b5d')\n    try:\n        print(f'Received {result.btc} / {result.rub} RUB.')\n    except telecoin.exceptions.InvalidCheque:\n        print('This is not a valid cheque.')\n\n\nif __name__ == '__main__':\n    asyncio.run(main())\n\n```\n\n---\n\n",
    'author': 'Marple',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/marple-git/telecoin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
