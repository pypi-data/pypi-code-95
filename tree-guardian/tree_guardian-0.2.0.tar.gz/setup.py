import os

from setuptools import setup, find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as file:
        return file.read()


setup(
    name='tree_guardian',
    version='0.2.0',
    keywords=['tree-guardian', 'observe', 'observer', 'directory', 'changes', ],
    url='https://github.com/fadich/tree-guardian',
    author='Fadi A.',
    author_email='royalfadich@gmail.com',
    description='Track the changes into the filesystem and trigger callback on changes detecting.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    requires=[
    ],
    scripts=[
        'tree_guardian/cli/tree-guardian-observe',
    ]
)
