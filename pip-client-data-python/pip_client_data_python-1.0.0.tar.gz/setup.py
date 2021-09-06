"""
Sample data microservice in Python
----------------------

This is a sample data microservice that stores and retries generic entities. This microservice shall be used
as a template to create general purpose data microservices.

Links
`````

* `development version <http://github.com/pip-services3-python/pip-services3-redis-python>`

"""

from setuptools import find_packages
from setuptools import setup

try:
    readme = open('readme.md').read()
except:
    readme = __doc__

setup(
    name='pip_client_data_python',
    version='1.0.0',
    url='https://github.com/pip-templates-services/pip-client-data-python',
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
        'pytest',

        'pip-services3-aws',
        'pip-services3-commons',
        'pip-services3-components',
        'pip-services3-container',
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
