# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lanim', 'lanim.examples']

package_data = \
{'': ['*']}

install_requires = \
['pillow>=8.3.2,<9.0.0']

setup_kwargs = {
    'name': 'lanim',
    'version': '0.1.0',
    'description': 'Functional animation library',
    'long_description': '# Requirements\n\n1. Python 3.9+\n2. Poetry\n3. Some external dependencies, see "External dependencies"\n\n# External dependencies\n\n## LaTeX\nLaTeX is needed to render text and equations.\n\n### Arch Linux\n```bash\nsudo pacman -S texlive-latexextra\n```\n\n### Ubuntu\n```\nsudo apt-get install texlive-latex-extra\n```\n\n### Windows\nYou should be good to go if you install MiKTeX (https://miktex.org/download)\n\n## FFmpeg\nFFmpeg is used to render a video from frames. You can get it here: https://www.ffmpeg.org/download.html\n\n\n# Usage\n\nCompile the example\n```bash\npython -m lanim -o out.mp4 lanim.examples.showcase\n```\n\nCompile the example in lower quality\n```bash\npython -m lanim -o out.mp4 -w 480 -h 270 --fps 15 lanim.examples.showcase\n```\n\nCompile the example but use tmpfs for temporary directory\n```bash\npython -m lanim -o out.mp4 -p /tmp/.lanim lanim.examples.showcase\n```\n\nSee full list of options:\n```bash\npython -m lanim --help\n```\n',
    'author': 'decorator-factory',
    'author_email': '42166884+decorator-factory@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/decorator-factory/lanim',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
