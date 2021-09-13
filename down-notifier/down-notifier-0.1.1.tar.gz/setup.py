# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['down_notifier', 'down_notifier.channel']

package_data = \
{'': ['*']}

install_requires = \
['aiogram>=2.14.3', 'aiohttp>=3.7.4']

setup_kwargs = {
    'name': 'down-notifier',
    'version': '0.1.1',
    'description': 'Send notification when your website is down.',
    'long_description': '# Down notifier\n\n## Usage\n\n```bash\npython -m down-notifier <config.json>\n```\n\nExample json config in "examples" folder.\n\n```python\nfrom down_notifier import Checker, Site\nfrom down_notifier.channel import TelegramChannel\n\nchannel = TelegramChannel(\n  name="channel_name",\n  message="{} - {}",\n  token="token",\n  chats=["chat_id_1", "chat_id_2"],\n)\nsite = Site(\n  name="site_name",\n  url="http://example.com",\n  status_code=200,\n  timeout=60,\n  channels=[channel],\n)\nchecker = Checker([site])\n\nchecker.start_loop()\n```\n',
    'author': 'pegov',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pegov/down-notifier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
