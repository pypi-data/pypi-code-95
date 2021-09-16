# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['augly_jp',
 'augly_jp.text',
 'augly_jp.text.augmenters',
 'augly_jp.text.functional',
 'augly_jp.text.transforms']

package_data = \
{'': ['*']}

install_requires = \
['augly>=0.1.6,<0.2.0',
 'chikkarpy>=0.1.0,<0.2.0',
 'dartsclone>=0.9.0,<0.10.0',
 'fugashi[unidic-lite]>=1.1.1,<2.0.0',
 'gensim>=4.0.1,<5.0.0',
 'ginza>=5.0.1,<6.0.0',
 'ja-ginza-electra>=5.0.0,<6.0.0',
 'numpy>=1.21.0,<2.0.0',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'tenacity>=8.0.1,<9.0.0',
 'tqdm>=4.62.2,<5.0.0',
 'transformers<4.10.0']

extras_require = \
{':sys_platform == "win32" or sys_platform == "darwin"': ['python-magic-bin>=0.4.14,<0.5.0']}

setup_kwargs = {
    'name': 'augly-jp',
    'version': '2021.9.17',
    'description': 'Data Augmentation for Japanese Text',
    'long_description': '# AugLy-jp\n> Data Augmentation for **Japanese Text** on AugLy\n\n[![PyPI Version][pypi-image]][pypi-url]\n[![Python Version][python-image]][python-image]\n[![Python Test][test-image]][test-url]\n[![Test Coverage][coverage-image]][coverage-url]\n[![Code Quality][quality-image]][quality-url]\n[![Python Style Guide][black-image]][black-url]\n\n## Augmenter\n`base_text = "あらゆる現実をすべて自分のほうへねじ曲げたのだ"`\n\nAugmenter | Augmented | Description\n:---:|:---:|:---:\nSynonymAugmenter|あらゆる現実をすべて自身のほうへねじ曲げたのだ|Substitute similar word according to [Sudachi synonym](https://github.com/WorksApplications/SudachiDict/blob/develop/docs/synonyms.md)\nWordEmbsAugmenter|あらゆる現実をすべて関心のほうへねじ曲げたのだ|Leverage word2vec, GloVe or fasttext embeddings to apply augmentation\nFillMaskAugmenter|つまり現実を、未来な未来まで変えたいんだ|Using masked language model to generate text\n\n## Prerequisites\n| Software                   | Install Command            |\n|----------------------------|----------------------------|\n| [Python 3.8.11][python]    | `pyenv install 3.8.11`     |\n| [Poetry 1.1.*][poetry]     | `curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py \\| python`|\n\n[python]: https://www.python.org/downloads/release/python-3811/\n[poetry]: https://python-poetry.org/\n\n## Get Started\n### Installation\n```bash\npip install augly-jp\n```\n\nOr clone this repository:\n```bash\ngit clone https://github.com/chck/AugLy-jp.git\npoetry install\n```\n\n### Test with reformat\n```bash\npoetry run task test\n```\n\n### Reformat\n```bash\npoetry run task fmt\n```\n\n### Lint\n```bash\npoetry run task lint\n```\n\n## Inspired\n- https://github.com/facebookresearch/AugLy\n- https://github.com/makcedward/nlpaug\n- https://github.com/QData/TextAttack\n\n## License\nThis software includes the work that is distributed in the Apache License 2.0 [[1]][apache1-url].\n\n[pypi-image]: https://badge.fury.io/py/augly-jp.svg\n[pypi-url]: https://badge.fury.io/py/augly-jp\n[python-image]: https://img.shields.io/pypi/pyversions/augly-jp.svg\n[test-image]: https://github.com/chck/AugLy-jp/workflows/Test/badge.svg\n[test-url]: https://github.com/chck/Augly-jp/actions?query=workflow%3ATest\n[coverage-image]: https://img.shields.io/codecov/c/github/chck/AugLy-jp?color=%2334D058\n[coverage-url]: https://codecov.io/gh/chck/AugLy-jp\n[quality-image]: https://img.shields.io/lgtm/grade/python/g/chck/AugLy-jp.svg?logo=lgtm&logoWidth=18\n[quality-url]: https://lgtm.com/projects/g/chck/AugLy-jp/context:python\n[black-image]: https://img.shields.io/badge/code%20style-black-black\n[black-url]: https://github.com/psf/black\n[apache1-url]: https://github.com/cl-tohoku/bert-japanese/blob/v2.0/LICENSE\n',
    'author': 'chck',
    'author_email': 'shimekiri.today@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chck/AugLy-jp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
