# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oshi', 'oshi.objects']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'oshi',
    'version': '0.1.0',
    'description': 'An asynchronous osu API wrapper written in python',
    'long_description': '# oshi\nAn asynchronous osu API wrapper made in python \n\n## Example(s)\n\n   ```py\n   import oshi\n   import asyncio\n\n\n   async def main() -> None:\n      auth = oshi.Authentication(CLIENT_ID, "CLIENT_SECRET")\n\n      async with oshi.Client(auth) as client:\n         map = await client.get_beatmap(id=1222063)\n         print(map.url)\n\n   asyncio.run(main())\n   ```\n\n\n## Development\n_For developers_\nIf you plan on contributing please open an issue beforehand\n\n## Contributors\n\n- [an-dyy](https://github.com/an-dyy) - creator and maintainer\n\n',
    'author': 'an-dyy',
    'author_email': 'andy.development@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/an-dyy/oshi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
