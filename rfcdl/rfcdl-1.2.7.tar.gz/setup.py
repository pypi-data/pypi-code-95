# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rfcdl']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.7.0,<0.8.0', 'aiohttp>=3.7.4,<4.0.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['rfcdl = rfcdl.rfcdl:main']}

setup_kwargs = {
    'name': 'rfcdl',
    'version': '1.2.7',
    'description': 'A tool for downloading RFCs in high-speed.',
    'long_description': '<div align="center">\n\t<h1>rfcdl</h1>\n\t<h4 align="center">\n\t\tAlways keep a copy of your favorite <a href="https://www.ietf.org/standards/rfcs/">RFCs</a>.\n\t</h4>\n\t<p>rfcdl lets you download and synchronize RCFs in high-speed.</p>\n</div>\n\n<p align="center">\n\t<a href="https://github.com/eikendev/rfcdl/actions"><img alt="Build status" src="https://img.shields.io/github/workflow/status/eikendev/rfcdl/Main"/></a>&nbsp;\n\t<a href="https://pypi.org/project/rfcdl/"><img alt="Development status" src="https://img.shields.io/pypi/status/rfcdl"/></a>&nbsp;\n\t<a href="https://github.com/eikendev/rfcdl/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/rfcdl"/></a>&nbsp;\n\t<a href="https://pypi.org/project/rfcdl/"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/rfcdl"/></a>&nbsp;\n\t<a href="https://pypi.org/project/rfcdl/"><img alt="Version" src="https://img.shields.io/pypi/v/rfcdl"/></a>&nbsp;\n\t<a href="https://pypi.org/project/rfcdl/"><img alt="Downloads" src="https://img.shields.io/pypi/dm/rfcdl"/></a>&nbsp;\n</p>\n\n## 🚀&nbsp;Installation\n\n### From PyPI\n\n```bash\npip install rfcdl\n```\n\n### From Source\n\n```bash\n./setup.py install\n```\n\n### Fedora\n\n```bash\nsudo dnf copr enable eikendev/rfcdl\nsudo dnf install python3-rfcdl\n```\n\n## 📄&nbsp;Usage\n\nThis tool can be used to download a large number of [RFC documents](https://www.ietf.org/standards/rfcs/) in a short period of time.\nI used it to keep a local mirror of all RFCs on my machines continuously synchronized.\n\nFor a quick introduction, let me show how you would use the tool to get started.\n\nThis is how you download the RFCs initially.\n\n```bash\nrfcdl -d ~/download/rfc/\n```\n\nAs can be seen above, you have to specify a directory where all RFC documents will be saved in.\nUpon the next invocation of `rfcdl`, only the RFCs missing in that directory will be downloaded.\n\nThis can then be combined with an alias that lets you read the local copy of any RFC.\nThe following command opens the RFC 8032 for me in less.\n\n```bash\nrfc 8032\n```\n\nCheck out [my dotfiles](https://github.com/eikendev/dotfiles/blob/199faa40873d8757a7c8f63d82d0f18a83b74ef9/source/zsh/function/rfc.zsh) to see how this is implemented.\n\n### Arguments\n\nIf you only want to download a random subset of all RFCs, use the `--samples` flag.\nThis can be used for testing.\nFor instance, the following will download 20 random RFC documents.\n\n```bash\nrfcdl -d ~/download/rfc/ --samples 20\n```\n\nSince `rfcdl` downloads multiple files in parallel by default, one can specify how many simultaneous downloads are allowed using the `--limit` flag.\nThe following invocation will only download at most ten files in parallel.\n\n```bash\nrfcdl -d ~/download/rfc/ --limit 10\n```\n\nTo explicitly state how many times `rfcdl` should download a file upon error, the `--retries` flag can be used.\nThis can be useful in case one expects a bad connection.\nThis is how you could tell the tool to try to download each file at maximum five times.\n\n```bash\nrfcdl -d ~/download/rfc/ --retries 5\n```\n\n## ⚙&nbsp;Configuration\n\nA configuration file can be saved to `~/.config/rfcdl/config.ini` to avoid specifying the path for each invocation.\nOf course, `$XDG_CONFIG_HOME` can be set to change your configuration path.\nAlternatively, the path to the configuration file can be set via the `--config-file` argument.\n\n```ini\n[GENERAL]\nRootDir = ~/download/rfc/\n```\n\n## 💻&nbsp;Development\n\nThe source code is located on [GitHub](https://github.com/eikendev/rfcdl).\nTo check out the repository, the following command can be used.\n\n```bash\ngit clone https://github.com/eikendev/rfcdl.git\n```\n',
    'author': 'eikendev',
    'author_email': 'raphael@eiken.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
