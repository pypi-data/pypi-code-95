# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['smqtk_descriptors',
 'smqtk_descriptors.impls',
 'smqtk_descriptors.impls.descriptor_element',
 'smqtk_descriptors.impls.descriptor_generator',
 'smqtk_descriptors.impls.descriptor_set',
 'smqtk_descriptors.interfaces',
 'smqtk_descriptors.utils']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.5,<2.0.0',
 'smqtk-core>=0.18.0',
 'smqtk-dataprovider>=0.16.0',
 'smqtk-image-io>=0.16.1,<0.17.0']

entry_points = \
{'smqtk_plugins': ['smqtk_descriptors.impls.descriptor_element.file = '
                   'smqtk_descriptors.impls.descriptor_element.file',
                   'smqtk_descriptors.impls.descriptor_element.memory = '
                   'smqtk_descriptors.impls.descriptor_element.memory',
                   'smqtk_descriptors.impls.descriptor_element.postgres = '
                   'smqtk_descriptors.impls.descriptor_element.postgres',
                   'smqtk_descriptors.impls.descriptor_element.solr = '
                   'smqtk_descriptors.impls.descriptor_element.solr',
                   'smqtk_descriptors.impls.descriptor_generator.caffe1 = '
                   'smqtk_descriptors.impls.descriptor_generator.caffe1',
                   'smqtk_descriptors.impls.descriptor_set.memory = '
                   'smqtk_descriptors.impls.descriptor_set.memory',
                   'smqtk_descriptors.impls.descriptor_set.postgres = '
                   'smqtk_descriptors.impls.descriptor_set.postgres',
                   'smqtk_descriptors.impls.descriptor_set.solr = '
                   'smqtk_descriptors.impls.descriptor_set.solr']}

setup_kwargs = {
    'name': 'smqtk-descriptors',
    'version': '0.17.0',
    'description': 'Algorithms, data structures and utilities around computingdescriptor vectors from data.',
    'long_description': '# SMQTK - Descriptors\n\n## Intent\nThis package aims to provide interfaces for algorithms and data structures\naround computing descriptor vectors from input data.\n\nThis package also includes a utility function that can map an arbitrary\nfunction to some set of input iterables, not unlike the python `map`, except\nthat this version is parallelized across threads or processes. This function\nalso does not block and may be used for parallelized stream processing.\n\n## Documentation\nYou can build the sphinx documentation locally for the most up-to-date\nreference:\n```bash\n# Install dependencies\npoetry install\n# Navigate to the documentation root.\ncd docs\n# Build the docs.\npoetry run make html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n',
    'author': 'Kitware, Inc.',
    'author_email': 'smqtk-developers@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kitware/SMQTK-Descriptors',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
