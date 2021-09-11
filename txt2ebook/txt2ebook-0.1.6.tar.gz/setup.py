# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['txt2ebook']

package_data = \
{'': ['*']}

install_requires = \
['EbookLib>=0.17.1,<0.18.0', 'Markdown>=3.3.4,<4.0.0', 'click>=8.0.1,<9.0.0']

entry_points = \
{'console_scripts': ['txt2ebook = txt2ebook.txt2ebook:main']}

setup_kwargs = {
    'name': 'txt2ebook',
    'version': '0.1.6',
    'description': 'Console tool to convert txt file to different ebook format',
    'long_description': '# txt2ebook\n\nConsole tool to convert txt file to different ebook format.\n\n## Installation\n\nFrom PyPI:\n\n```\npip install txt2ebook\n```\n\n## Usage\n\nShowing help message:\n\n```bash\n$ txt2ebook\nUsage: txt2ebook [OPTIONS] FILENAME\n\n  Console tool to convert txt file to different ebook format.\n\nOptions:\n  -t, --title TEXT                Set the title of the ebook.\n  -l, --language TEXT             Set the language of the ebook.  [default:\n                                  en]\n  -a, --author TEXT               Set the author of the ebook.\n  -d, --debug                     Enable debugging log.\n  -nb, --no-backup                Do not backup source txt file.  [default:\n                                  False]\n  -rw, --remove_wrapping          Remove word wrapping.  [default: False]\n  -dr, --delete-regex TEXT        Regex to delete word or phrase.\n  -rr, --replace-regex TEXT...    Regex to replace word or phrase.\n  -dlr, --delete-line-regex TEXT  Regex to delete whole line.\n  --version                       Show the version and exit.\n  --help                          Show this message and exit.\n```\n\nConvert a txt file into epub:\n\n```bash\ntxt2book ebook.txt\n```\n\n## Copyright and License\n\nCopyright (c) 2021 Kian-Meng, Ang\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU Affero General Public License as\npublished by the Free Software Foundation, either version 3 of the\nLicense, or (at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU Affero General Public License for more details.\n\nYou should have received a copy of the GNU Affero General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/>.\n',
    'author': 'Kian-Meng Ang',
    'author_email': 'kianmeng@cpan.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kianmeng/txt2ebook',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
