"""
Pip.Services DataDog
----------------------

Pip.Services is an open-source library of basic microservices.
pip_services3_datadog provides synchronous and asynchronous communication components.

Links
`````

* `website <http://github.com/pip-services-python/>`_
* `development version <http://github.com/pip-services3-python/pip-services3-aws-python>`

"""

from setuptools import setup
from setuptools import find_packages

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='pip_services3_datadog',
    version='3.0.0',
    url='http://github.com/pip-services3-python/pip-services3-datadog-python',
    license='MIT',
    author='Conceptual Vision Consulting LLC',
    author_email='seroukhov@gmail.com',
    description='Communication components for Pip.Services in Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['config', 'data', 'test']),
    include_package_data=True,
    zip_safe=True,
    platforms='any',
    install_requires=[
        'pip-services3-commons',
        'pip-services3-components',
        'pip-services3-rpc'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
