# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smqtk_core']

package_data = \
{'': ['*']}

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.7,<4.0']}

setup_kwargs = {
    'name': 'smqtk-core',
    'version': '0.18.1',
    'description': 'Python toolkit for pluggable algorithms and data structures for multimedia-based machine learning.',
    'long_description': '# SMQTK - Core\n\nA light-weight, non-intrusive framework for developing interfaces that have\nbuilt-in implementation discovery and factory construction from a simple\nconfiguration structure.\n\nWhile anything may make use of this library, this was originally developed\nas a foundation for a suite of packages that predominantly support **AI** and\n**Machine Learning** use-cases:\n\n* Scalable data structure interfaces and implementations, with a focus on those\n  relevant for machine learning like descriptors, classifications, and object\n  detections.\n\n* Interfaces and implementations of machine learning algorithms with a focus on\n  media-based functionality.\n****\n## Libraries\nSome above-mentioned packages supporting AI/ML topics include the following:\n\n* [SMQTK-Dataprovider] provides\n  abstractions around data storage and retrieval.\n\n* [SMQTK-Image-IO] provides\n  interfaces and implementations around image reading and writing using\n  abstractions defined in [SMQTK-Dataprovider].\n\n* [SMQTK-Descriptors] provides\n  algorithms and data structures around computing descriptor vectors from\n  different kinds of input data.\n\n* [SMQTK-Classifier] provides\n  interfaces and implementations around black-box classification.\n\n* [SMQTK-Indexing] provides\n  interfaces and implementations for efficient, large-scale indexing of\n  descriptor vectors.\n  The sources of such descriptor vectors may come from a multitude of sources,\n  such as hours of video archives.\n  Some provided implementation plugins include [Locality-sensitive Hashing\n  (LSH)](https://en.wikipedia.org/wiki/Locality-sensitive_hashing) and FAIR\'s\n  [FAISS] library.\n\n* [SMQTK-Relevancy] provides\n  interfaces and implementations for ranking datasets using human-in-the-loop\n  feedback.\n  This is a primary component for Interactive Query Refinement (IQR) systems\n  that makes use of human feedback.\n\nThese packages are related as followed:\n![Dependency Graph](docs/images/dep_block.svg)\n\n## This looks a lot like KWIVER! Why use this instead?\n[KWIVER] is another open source package that similarly holds modularity,\nplugins and configurability at its core.\n\nThe SMQTK-* suite of functionality exists separately from KWIVER for a few\nreasons (for now):\n* History\n  * The origins of KWIVER and SMQTK were initiated at roughly the same\n    time and were never resolved into the same thing because...\n* Language\n  * KWIVER has historically been predominantly C++ while SMQTK-* is (mostly)\n    pure python. (see note below)\n* Configuration UX\n  * SMQTK takes an "add on" approach to configurability: concrete\n    implementations have parameterized constructors and should be usable after\n    construction like a "normal" object.\n    Configuration semantics are derived from introspection of, and explicitly\n    related to, the constructor.\n    KWIVER takes an alternative approach where construction is generally empty\n    and configuration setting is a required separate step via a custom object\n    (`ConfigBlock`).\n* Pythonic Plugin Support\n  * Plugins are exposed via standard package entrypoints.\n\n> If I\'m using python, does that mean that SMQTK is __*always*__ the better\n> choice?\n\nAt this point, not necessarily.\nWhile this used to be true for a number of years due to SMQTK being the toolkit\nwith python support.\nThis is becoming more blurry KWIVER\'s continuously improving python binding\nsupport.\n\n## Building Documentation\nDocumentation is [hosted on ReadTheDocs.io here](\nhttps://smqtk-core.readthedocs.io/en/stable/).\n\nYou can also build the sphinx documentation locally for the most up-to-date\nreference:\n```bash\n# Install dependencies\npoetry install\n# Navigate to the documentation root.\ncd docs\n# Build the docs.\npoetry run make html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n\n\n[FAISS]: https://github.com/facebookresearch/faiss\n[KWIVER]: https://github.com/kitware/kwiver\n[SMQTK-Dataprovider]: https://github.com/Kitware/SMQTK-Dataprovider\n[SMQTK-Image-IO]: https://github.com/Kitware/SMQTK-Image-IO\n[SMQTK-Descriptors]: https://github.com/Kitware/SMQTK-Descriptors\n[SMQTK-Classifier]: https://github.com/Kitware/SMQTK-Classifier\n[SMQTK-Indexing]: https://github.com/Kitware/SMQTK-Indexing\n[SMQTK-Relevancy]: https://github.com/Kitware/SMQTK-Relevancy\n',
    'author': 'Kitware, Inc.',
    'author_email': 'smqtk-developers@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kitware/SMQTK-Core',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
