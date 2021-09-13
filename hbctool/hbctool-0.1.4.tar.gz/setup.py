# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hbctool',
 'hbctool.hbc',
 'hbctool.hbc.hbc59',
 'hbctool.hbc.hbc59.tool',
 'hbctool.hbc.hbc74',
 'hbctool.hbc.hbc74.tool',
 'hbctool.hbc.hbc76',
 'hbctool.hbc.hbc76.tool']

package_data = \
{'': ['*'],
 'hbctool.hbc.hbc59': ['data/*', 'example/*', 'raw/*'],
 'hbctool.hbc.hbc74': ['data/*', 'example/*', 'raw/*'],
 'hbctool.hbc.hbc76': ['data/*', 'example/*', 'raw/*']}

install_requires = \
['docopt>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['hbctool = hbctool:main']}

setup_kwargs = {
    'name': 'hbctool',
    'version': '0.1.4',
    'description': 'A command-line interface for disassembling and assembling the Hermes Bytecode.',
    'long_description': "# hbctool \n\n[![Python 3.x](https://img.shields.io/badge/python-3.x-yellow.svg)](https://python.org) [![PyPI version](https://badge.fury.io/py/hbctool.svg)](https://badge.fury.io/py/hbctool) [![Software License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](/LICENSE)\n\nA command-line interface for disassembling and assembling the Hermes Bytecode.\n\nSince the React Native team created their own JavaScript engine (named Hermes) for running the React Native application, the JavaScript source code is often compiled to the Hermes bytecode. In the penetration test project, I found that some React Native applications have already been migrated to the Hermes engine. It is really head for me to analyze or patch those applications. Therefore, I created hbctool for helping any pentester to test the Hermes bytecode.\n\n> [Hermes](https://hermesengine.dev/) is an open-source JavaScript engine optimized for running React Native apps on Android. For many apps, enabling Hermes will result in improved start-up time, decreased memory usage, and smaller app size. At this time Hermes is an opt-in React Native feature, and this guide explains how to enable it.\n\nSpecial thanks to [ErbaZZ](https://github.com/ErbaZZ) and [Jusmistic](https://github.com/Jusmistic) for helping me research and develop this tool.\n\nFor more information, please visit:\n\n[https://suam.wtf/posts/react-native-application-static-analysis-en/](https://suam.wtf/posts/react-native-application-static-analysis-en/)\n\n## Screenshot\n\n![hbctool Example](/image/hbctool_example.gif)\n\nThis video with MP4 format can be found at [/image/hbctool_example.mp4](/image/hbctool_example.mp4).\n\n## Installation\n\nTo install hbctool, simply use pip:\n\n```\npip install hbctool\n```\n\n## Usage\n\nPlease run `hbctool --help` to show the usage.\n\n```\nhbctool --help   \nA command-line interface for disassembling and assembling\nthe Hermes Bytecode.\n\nUsage:\n    hbctool disasm <HBC_FILE> <HASM_PATH>\n    hbctool asm <HASM_PATH> <HBC_FILE>\n    hbctool --help\n    hbctool --version\n\nOperation:\n    disasm              Disassemble Hermes Bytecode\n    asm                 Assemble Hermes Bytecode\n\nArgs:\n    HBC_FILE            Target HBC file\n    HASM_PATH           Target HASM directory path\n\nOptions:\n    --version           Show hbctool version\n    --help              Show hbctool help manual\n\nExamples:\n    hbctool disasm index.android.bundle test_hasm\n    hbctool asm test_hasm index.android.bundle\n```\n\n> For Android, the HBC file normally locates at `assets` directory with `index.android.bundle` filename.\n\n## Support\n\nhbctool currently supports the following Hermes Bytecode version:\n\n- [Hermes Bytecode version 59](/hbctool/hbc/hbc59/)\n- [Hermes Bytecode version 74](/hbctool/hbc/hbc74/)\n- [Hermes Bytecode version 76](/hbctool/hbc/hbc76/)\n\n## Contribution\n\nFeel free to create an issue or submit the merge request. Anyway you want to contribute this project. I'm very happy about it.\n\nHowever, please run the unit test before submiting the pull request.\n\n```\ncd hbctool\npython test.py\n```\n\nI use poetry to build this tool. To build it yourself, simply execute:\n\n```\npoetry install\n```\n\n## Next Step\n\n- Add the other Hermes bytecode versions\n- Create a class abstraction\n- Support overflow patching\n- Do all TODO, NOTE, FIXME in source code\n",
    'author': 'bongtrop',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bongtrop/hbctool',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
