# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bookmarkdown']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['btm = bookmarkdown.btm:main']}

setup_kwargs = {
    'name': 'bookmarkdown',
    'version': '0.1.1',
    'description': "Parse your browser's exported HTML bookmark file to Markdown.",
    'long_description': '# bookmarkdown\n\nParse your browser\'s exported HTML bookmark file to Markdown.\n\nSupported browsers: Brave.\n\n## Installation\n\n```bash\npip install bookmarkdown\n```\n\n## Usage\n\n### CLI\n\n```bash\n# Convert "bookmarks.html" to markdown and output to STDOUT\nbtm bookmarks.html\n\n# Convert "bookmarks.html" to markdown and write to "bookmarks.md"\nbtm --output=bookmarks.md bookmarks.html\n\n# Alternatively\nbtm bookmarks.html > bookmarks.md\n```\n\n### Python\n\nThe `BookmarkHTMLParser` is an instance of the Python standard library\'s\n[`HTMLParser`](https://docs.python.org/3/library/html.parser.html) and thus supports all its\nmethods.\n\n```python\nfrom bookmarkdown import btm\n\nparser = btm.BookmarkHTMLParser()\nparser.feed(html_content)\n\n# Access the data\nparser.data\n```\n\n## FAQ\n\n### Concerns\n\n* Minimal dependencies. `bookmarkdown` is likely to be installed on the system level Python to make\n  use of the `btm` script.\n* Correctness. No one likes to lose a bookmark nor a different ordering.\n\n### Future ideas\n\n> The current application solves my needs pretty well, but there are additional applications I can\n> think of. Such as merging multiple bookmark files.\n\nAdd functionality to the CLI and Python codebase to support the following:\n\n```bash\n# Merge bookmark html-file into existing markdown file.\nbtm --merge=[md-file] [html-file]\n\nbtm [html-file]  # already implemented\n\n# Read the `-r` as "reverse", i.e. instead of bookmark to markdown it\n# becomes markdown to bookmark.\nbtm -r [md-file]\n\nbtm -r --merge=[md-file] [html-file]\n```\n\n### Project structure\n\nThe project structure was automatically set up using `cookiecutter` and my Python template:\n[cutter-py](https://github.com/yannickperrenet/cutter-py).\n',
    'author': 'Yannick Perrenet',
    'author_email': 'yannickperrenet+bookmarkdown@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/yannickperrenet/bookmarkdown',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
