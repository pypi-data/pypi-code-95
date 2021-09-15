# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['randiter']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'randiter',
    'version': '0.1.0',
    'description': 'Randomly iterate a sequence with buffered shuffling',
    'long_description': '# randiter\n\n`randiter` randomly iterates a sequence with buffered shuffling.\n`randiter` is suitable for shuffling very long sequences and sequences with an unknown length.\n\n## Usage\n\nShuffle a very long sequence:\n\n```python\nfrom randiter import randiter\n\nfor index in randiter(range(1_000_000_000)):\n    print(index)  # random number\n```\n\nShuffle lines in a text file with an unknown length:\n\n```python\nfrom randiter import randiter\n\nwith open("large.txt", "rt") as f:\n    for line in randiter(f):\n        print(line)  # random line\n```\n\nShuffle a sequence with a large buffer size (to perform perfect shuffling, specify a buffer size that is equal to or greater than the length of the given sequence):\n\n```python\nfrom randiter import randiter\n\nfor index in randiter(range(1_000_000_000), buffer_size=1_000_000):\n    print(index)  # random number\n```\n\n## FAQ\n\n- Q. Shuffled sequences are not completely shuffled.\n  - A. This is because `randiter` performs *buffered* shuffling. This problem can be mitigated by specifying a larger buffer size.\n',
    'author': 'Hirokazu Kiyomaru',
    'author_email': 'h.kiyomaru@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hkiyomaru/randiter',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
