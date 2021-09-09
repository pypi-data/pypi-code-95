# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['epicnumbers']

package_data = \
{'': ['*']}

install_requires = \
['tabulate>=0.8.8,<0.9.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.4.0,<4.0.0']}

entry_points = \
{'console_scripts': ['en = epicnumbers.main:main',
                     'epicnumbers = epicnumbers.main:main']}

setup_kwargs = {
    'name': 'epicnumbers',
    'version': '1.1.0',
    'description': 'A tool to convert numbers into various other formats and different sized integers',
    'long_description': '# epicnumbers\n\nA small tool I often used to convert a number into various other formats\n\n# Usage\n\n```bash\n$ pip install epicnumbers\n```\n\n```bash\n$ epicnumbers <number>\n```\n\n# Examples\n\nConvert -100 into signed, unsigned, hex, printable and binary in different sized integers\n```\n$ en -100\ntype      signed              unsigned  hex                  printable                         binary\n------  --------  --------------------  -------------------  --------------------------------  -----------------------------------------------------------------------\n8 bit       -100                   156  0x9c                 \\x9c                              10011100\n16 bit      -100                 65436  0xff9c               \\x9c\\xff                          11111111 10011100\n32 bit      -100            4294967196  0xffffff9c           \\x9c\\xff\\xff\\xff                  11111111 11111111 11111111 10011100\n64 bit      -100  18446744073709551516  0xffffffffffffff9cL  \\x9c\\xff\\xff\\xff\\xff\\xff\\xff\\xff  11111111 11111111 11111111 11111111 11111111 11111111 11111111 10011100\n```\n\nConvert 0x100 into signed, unsigned, hex, printable and binary in different sized integers\n```\n$ en 100h\ntype      signed    unsigned  hex    printable                         binary\n------  --------  ----------  -----  --------------------------------  ----------\n16 bit       256         256  0x100  \\x00\\x01                          1 00000000\n32 bit       256         256  0x100  \\x00\\x01\\x00\\x00                  1 00000000\n64 bit       256         256  0x100  \\x00\\x01\\x00\\x00\\x00\\x00\\x00\\x00  1 00000000\n```\n\nConvert 100b (binary) into signed, unsigned, hex, printable and binary in different sized integers\n```\n$ en 100b\ntype      signed    unsigned  hex    printable                           binary\n------  --------  ----------  -----  --------------------------------  --------\n8 bit          4           4  0x4    \\x04                                   100\n16 bit         4           4  0x4    \\x04\\x00                               100\n32 bit         4           4  0x4    \\x04\\x00\\x00\\x00                       100\n64 bit         4           4  0x4    \\x04\\x00\\x00\\x00\\x00\\x00\\x00\\x00       100\n```\n\n# Development\n\n1. install [poetry](https://python-poetry.org/)\n2. `$ poetry install`\n3. `$ poetry shell`\n\n## Run tests\n\n```bash\n$ poetry run pytest\n```\n\n## Run tool\n\n```bash\n$ poetry run en 100h\n```\n',
    'author': 'Henrik Nårstad',
    'author_email': 'henriknaa@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/narhen/epicnumbers',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
