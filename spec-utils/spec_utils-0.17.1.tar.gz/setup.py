from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='spec_utils',
    version='0.17.1',
    description='Python package to consume SPEC SA and third-party apps',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],

    long_description=long_description,
    long_description_content_type='text/markdown',

    install_requires=[
        'requests',
        'pandas',
        'sqlalchemy',
        'pydantic'
    ],

    extra_require={
        'dev': [
            'pytest>=3.8',
        ],
    },

    url='https://gitlab.com/spec-sa-ar/spec-utils',
    author='Lucas Lucyk',
    author_email='llucyk@grupospec.com',
)
