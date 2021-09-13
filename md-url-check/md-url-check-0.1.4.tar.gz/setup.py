# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['md_url_check']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['md-url-check = md_url_check.__main__:cli']}

setup_kwargs = {
    'name': 'md-url-check',
    'version': '0.1.4',
    'description': 'Simple CLI tool to check URL health in markdown files.',
    'long_description': '<div align="center">\n\n<h1>Markdown URL Checker</h1>\n<strong>>> <i>Simple CLI tool to check URL health in markdown files</i> <<</strong>\n\n&nbsp;\n\n![img](./art/logo.png)\n\n</div>\n\n\nThis CLI tool traverses down a markdown file, extracts all the valid URLs, and checks whether they\'re accessible or not. In case it encounters a broken link, it raises an error. Internally, this is optimized for larger markdown files and tested for huge markdown files with thousands of links.\n\n## Installation\n\nInstall the CLI using pip:\n\n```\npip install md-url-checker\n```\n\n\n## Usage\n\n* To check the URLs in a single markdown file, run:\n\n    ```\n    md-url-check -f file.md\n    ```\n\n* To check the URLs in multiple markdown files, run:\n\n    ```\n    echo \'file1.md file2.md\' | xargs -n 1 md-url-check -f\n    ```\n\n* To check the URLs in multiple files in a folder, run:\n\n    ```\n    find . -name \'*.md\' | xargs -n 1 --no-run-if-empty md-url-check -f\n    ```\n\n* Suppress intermediate output:\n\n    ```\n    md-url-check -f file.md -s\n    ```\n\n* Provide the number of threads to be used while making the requests:\n\n    ```\n    md-url-check -f file.md -s -t 32\n    ```\n\n    This uses 32 interleaving threads to make the requests concurrently. Default is 8.\n\n\n<div align="center">\n<i> ✨ 🍰 ✨ </i>\n</div>\n',
    'author': 'Redowan Delowar',
    'author_email': 'redowan.nafi@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rednafi/md-url-check',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
