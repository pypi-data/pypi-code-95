# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['iytdl', 'iytdl.types', 'iytdl.upload_lib']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.1,<9.0.0',
 'Pyrogram>=1.2.9,<2.0.0',
 'TgCrypto>=1.2.2,<2.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'hachoir>=3.1.2,<4.0.0',
 'html-telegraph-poster>=0.4.0,<0.5.0',
 'mutagen>=1.45.1,<2.0.0',
 'youtube-search-python==1.4.6',
 'yt-dlp>=2021.9.2,<2022.0.0']

setup_kwargs = {
    'name': 'iytdl',
    'version': '0.5.2',
    'description': 'Aysnc Inline YouTube-DL for Pyrogram',
    'long_description': '<p align="center">\n<img src="https://i.imgur.com/Q94CDKC.png" width=250px>\n\n# iYTDL\n\n<a href="https://github.com/iytdl/iytdl/blob/main/LICENSE"><img alt="License: GPLv3" src="https://img.shields.io/badge/License-GPLv3-blue.svg"></a>\n<a href="https://github.com/iytdl/iytdl/actions"><img alt="Actions Status" src="https://github.com/iytdl/iytdl/actions/workflows/pypi-publish.yaml/badge.svg"></a>\n<a href="https://pypi.org/project/iytdl/"><img alt="PyPI" src="https://img.shields.io/pypi/v/iytdl"></a>\n<a href="https://pepy.tech/project/iytdl"><img alt="Downloads" src="https://pepy.tech/badge/iytdl"></a>\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n\n</p>\n\n<h2 align="center"> Aysnc Inline YouTube-DL for Pyrogram</h2>\n\n## ⬇️ Installation\n\n> Install\n\n```bash\npip3 install iytdl\n```\n\n> Upgrade\n\n```bash\npip3 install -U iytdl\n```\n\n> Build Wheel Locally\n\n```bash\ngit clone https://github.com/iytdl/iytdl.git\ncd iytdl\npoetry install\n\nchmod +x scripts/install.sh && ./scripts/install.sh\n```\n\n## Features\n\n- Async and memory efficient (uses Aiosqlite for Caching)\n- Uses hashing avoid storing duplicate data\n- Supports context manager\n- Supports External Downloader [[Aria2c](https://github.com/iytdl/iytdl/blob/master/tests/test_download_upload.py#L20)]\n- [Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)\n\n## Requirements\n\n- [YT-DLP](https://github.com/yt-dlp/yt-dlp) (Active youtube-dl fork)\n- [Python](https://www.python.org/) >=3.8,<4\n- [Pyrogram](https://docs.pyrogram.org/) based Bot\n- [FFmpeg](http://ffmpeg.org/)\n- [Aria2c](https://aria2.github.io/) (_Optional_)\n\n## Pre-commit Hooks\n\n- [Install Pre-commit Hooks](https://pre-commit.com/#installation)\n- `pre-commit install`\n\n## Examples\n\n### Callbacks\n\n<details>\n  <summary><b>OPEN</b></summary>\n\n- Back and Next\n\n```python\nr"^yt_(back|next)\\|(?P<key>[\\w-]{5,11})\\|(?P<pg>\\d+)$"\n```\n\n- List View\n\n```python\nr"^yt_listall\\|(?P<key>[\\w-]{5,11})$"\n```\n\n- Extract Info\n\n```python\nr"^yt_extract_info\\|(?P<key>[\\w-]{5,11})$"\n```\n\n- Download\n\n```python\nr"yt_(?P<mode>gen|dl)\\|(?P<key>[\\w-]+)\\|(?P<choice>[\\w-]+)\\|(?P<dl_type>a|v)$"\n```\n\n- Cancel\n\n```python\nr"^yt_cancel\\|(?P<process_id>[\\w\\.]+)$"\n```\n\n</details>\n\n### Module\n\n### [YouTube.py](https://github.com/code-rgb/droid/blob/master/droid/modules/youtube.py)\n',
    'author': 'Leorio Paradinight',
    'author_email': '62891774+code-rgb@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/iytdl/iytdl',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
