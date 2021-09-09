#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'docker>=5',
				'greenlet>=1',  'pycryptodome>=3', 
				'sqlalchemy>=1.4', 'teradataml>=17',
				'teradatasql>=17', 'teradatasqlalchemy>=17',
				'websocket-client>=1.2']

test_requirements = ['pytest>=3', ]

setup(
    author="Denis Molin",
    author_email='denis.molin@teradata.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="demo energy consumption shows how to seamlessly leverage Teradata Vantage in your Python projects.",
    entry_points={
        'console_scripts': [
            'demo_energy_consumption=demo_energy_consumption.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='demo_energy_consumption',
    name='demo_energy_consumption',
    packages=find_packages(include=['demo_energy_consumption', 'demo_energy_consumption.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/denismolin/demo_energy_consumption',
    version='0.2.3',
    zip_safe=False,
)
