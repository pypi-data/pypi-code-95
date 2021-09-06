# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['quickhttp']

package_data = \
{'': ['*']}

install_requires = \
['pytimeparse>=1.1.8,<2.0.0', 'typer>=0.3.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0']}

entry_points = \
{'console_scripts': ['quickhttp = quickhttp.cli:app']}

setup_kwargs = {
    'name': 'quickhttp',
    'version': '1.0.0',
    'description': "Lightweight CLI that wraps Python's http.server with automatic port-finding and shutdown.",
    'long_description': "# quickhttp\n\n[![Docs Status](https://img.shields.io/badge/docs-stable-informational)](https://jayqi.github.io/quickhttp/)\n[![PyPI](https://img.shields.io/pypi/v/quickhttp.svg)](https://pypi.org/project/quickhttp/)\n[![tests](https://github.com/jayqi/quickhttp/workflows/tests/badge.svg?branch=main)](https://github.com/jayqi/quickhttp/actions?query=workflow%3Atests+branch%3Amain)\n[![codecov](https://codecov.io/gh/jayqi/quickhttp/branch/main/graph/badge.svg)](https://codecov.io/gh/jayqi/quickhttp)\n\n`quickhttp` is a lightweight CLI that wraps Python's `http.server` with automatic port-finding and automatic shutdown after a configurable idle duration.\n\n## Features\n\n- Automatically finds and uses an available port.\n- Has a keep-alive time after which it will shut down automatically if no requests are received, in case you forget about it.\n- More secure default of `127.0.0.1` (`localhost`) instead of `0.0.0.0`.\n- Easier to type and autocomplete than `python -m http.server`.\n\n## Installation\n\nYou can get `quickhttp` from [PyPI](https://pypi.org/project/quickhttp/). I recommend using [`pipx`](https://pipxproject.github.io/pipx/) to manage Python command-line programs:\n\n```bash\npipx install quickhttp\n```\n\nYou can also install normally using regular `pip`:\n\n```bash\npip install quickhttp\n```\n\nRequires Python 3.6 or higher.\n\n### Development Version\n\nTo install the development version of this program, get it directly from GitHub.\n\n```bash\npipx install git+https://github.com/jayqi/quickhttp.git\n```\n\n## Documentation\n\n```bash\nquickhttp --help\n```\n\n```text\nUsage: quickhttp [OPTIONS] [DIRECTORY]\n\n  Lightweight CLI that wraps Python's `http.server` with automatic port-\n  finding and shutdown.\n\nArguments:\n  [DIRECTORY]  Directory to serve.  [default: .]\n\nOptions:\n  -t, --timeout TEXT              Time to keep server alive for after most\n                                  recent request. Accepts time expressions\n                                  parsable by pytime parse, such as '10m' or\n                                  '10:00'.  [default: 10m]\n\n  -b, --bind TEXT                 Address to bind server to. '127.0.0.1' (or\n                                  'localhost') will only be accessible from\n                                  this computer. '0.0.0.0' is all interfaces\n                                  (IP addresses) on this computer, meaning\n                                  that it can be accessible by other computers\n                                  at your IP address.  [default: 127.0.0.1]\n\n  -p, --port INTEGER              Port to use. If None (default), will\n                                  automatically search for an open port using\n                                  the other port-related options. If\n                                  specified, ignores other port-related\n                                  options.\n\n  --port-range-min INTEGER        Minimum of range to search for an open port.\n                                  [default: 8000]\n\n  --port-range-max INTEGER        Maximum of range to search for an open port.\n                                  [default: 8999]\n\n  --port-max-tries INTEGER        Maximum number of ports to check.  [default:\n                                  50]\n\n  --port-search-type [sequential|random]\n                                  Type of search to use.  [default:\n                                  sequential]\n\n  --version                       Show version and exit.\n  --install-completion [bash|zsh|fish|powershell|pwsh]\n                                  Install completion for the specified shell.\n  --show-completion [bash|zsh|fish|powershell|pwsh]\n                                  Show completion for the specified shell, to\n                                  copy it or customize the installation.\n\n  --help                          Show this message and exit.\n```\n\n## Why use `quickhttp`?\n\n- `python -m http.server` is a pain to type. `quickhttp` is shorter and can autocomplete. (But you can still do `python -m quickhttp` too if you really want to.)\n- If you try starting `python -m http.server` and port 8000 is unavailable, you get `OSError: [Errno 48] Address already in use`. Then you have to choose another port and try again. `quickhttp` deals with ports automatically for you.\n- `quickhttp` will automatically shutdown after the keep-alive time expires. This defaults to 10 minutes. I often start up an HTTP server to look at something, then open a new tab to continue doing things, and then I forget about the server.\n- `python -m http.server` defaults to 0.0.0.0, which may make your server accessible to other people at your computer's IP address. This is a security vulnerability, but isn't necessarily obvious to people who just want to quickly serve some static files.\n",
    'author': 'Jay Qi',
    'author_email': 'jayqi.opensource@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jayqi/quickhttp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
