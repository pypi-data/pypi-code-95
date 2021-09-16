# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smqtk_classifier',
 'smqtk_classifier.impls',
 'smqtk_classifier.impls.classification_element',
 'smqtk_classifier.impls.classify_descriptor',
 'smqtk_classifier.impls.classify_descriptor_supervised',
 'smqtk_classifier.interfaces']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.5,<2.0.0',
 'smqtk-core>=0.18.0',
 'smqtk-dataprovider>=0.16.0',
 'smqtk-descriptors>=0.16.0']

extras_require = \
{'sklearn': ['scikit-learn>=0.24.1,<0.25.0']}

entry_points = \
{'smqtk_plugins': ['smqtk_classifier.impls.classification_element.file = '
                   'smqtk_classifier.impls.classification_element.file',
                   'smqtk_classifier.impls.classification_element.memory = '
                   'smqtk_classifier.impls.classification_element.memory',
                   'smqtk_classifier.impls.classification_element.postgres = '
                   'smqtk_classifier.impls.classification_element.postgres',
                   'smqtk_classifier.impls.classify_descriptor.classify_index_label_descriptor '
                   '= '
                   'smqtk_classifier.impls.classify_descriptor.classify_index_label_descriptor',
                   'smqtk_classifier.impls.classify_descriptor_supervised.libsvm '
                   '= '
                   'smqtk_classifier.impls.classify_descriptor_supervised.libsvm',
                   'smqtk_classifier.impls.classify_descriptor_supervised.sklearn_logistic_regression '
                   '= '
                   'smqtk_classifier.impls.classify_descriptor_supervised.sklearn_logistic_regression']}

setup_kwargs = {
    'name': 'smqtk-classifier',
    'version': '0.18.0',
    'description': 'Algorithms, data structures and utilities around performing classificationof inputs.',
    'long_description': '# SMQTK - Classifier\n\n## Intent\nThis package provides interfaces and implementations around the classification\nof inputs into some form of labeled probabilistic values.\nAdditional data structure abstractions are defined here to standardize this\nbehavior into common terms.\n\n## Documentation\nYou can build the sphinx documentation locally for the most up-to-date\nreference:\n```bash\n# Install dependencies\npoetry install\n# Navigate to the documentation root.\ncd docs\n# Build the docs.\npoetry run make html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n',
    'author': 'Kitware, Inc.',
    'author_email': 'smqtk-developers@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kitware/SMQTK-Classifier',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
