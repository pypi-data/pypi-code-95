#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from setuptools import setup

# Dynamically calculate the version based on textrank.VERSION.
version = __import__('textrank').get_version()

with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='django-textrank',
    version=version,
    description=(
        'This is a Django reusable application for ranging a text by keywords.'
    ),
    long_description=long_description,
    author='Grigoriy Kramarenko',
    author_email='root@rosix.ru',
    url='https://gitlab.com/djbaldey/django-textrank/',
    license='BSD License',
    platforms='any',
    zip_safe=False,
    packages=['textrank'],
    include_package_data=True,
    install_requires=[
        'django>=2.2',
        'djangokit>=0.1',
        'pymorphy2>=0.8',
    ],
    classifiers=[
        # List of Classifiers: https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Russian',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
