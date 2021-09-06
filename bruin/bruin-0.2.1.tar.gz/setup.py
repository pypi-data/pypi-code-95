from setuptools import setup, find_packages
from io import open
from os import path
import pathlib

CURDIRT = pathlib.Path(__file__).parent

README = (CURDIRT / "README.md").read_text()

with open(path.join(CURDIRT, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (not x.startswith("#"))]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='bruin',
    description="Command line tool made by python for various toolbox used in UCLA",
    version="0.2.1",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires='>=3.6',
    entry_points='''
        [console_scripts]
        bruin=bruin.__main__:main
    ''',
    include_package_data=True,
    dependency_links=dependency_links,
    license='MIT',
    author='Oswald He',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/OswaldHe/bruin-cli"
)