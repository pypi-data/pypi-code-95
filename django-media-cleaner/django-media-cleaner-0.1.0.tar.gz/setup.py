
#!/usr/bin/env python

import os
import re
from codecs import open as codecs_open

from setuptools import find_packages, setup


def read(*parts):
    file_path = os.path.join(os.path.dirname(__file__), *parts)
    return codecs_open(file_path, encoding='utf-8').read()



setup(
    name='django-media-cleaner',
    version='0.1.0',
    packages=['django_media_cleaner'],
    include_package_data=True,
    requires=['python (>=3.8)', 'django (>=3.2)'],
    description='Searches and removes unused media files.',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    author='Ilya Shalyapin',
    author_email='ishalyapin@gmail.com',
    url='https://github.com/un1t/django-media-cleaner',
    download_url='https://github.com/un1t/django-media-cleaner/tarball/master',
    license='MIT License',
    keywords='django',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
)