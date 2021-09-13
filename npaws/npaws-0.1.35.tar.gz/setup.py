from setuptools import setup, find_packages
import pathlib


def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]

reqs = parse_requirements('requirements.txt')
# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()


setup(
    name='npaws',
    packages=find_packages(),
    description='An SDK that provides functionalities for Neural Platform Project.',
    long_description=README,
    version='0.1.35',
    url='https://github.com/miquelescobar/npaws',
    author='Miquel Escobar',
    author_email='miquel.escobar@bsc.es',
    keywords=['pip','neural','platform','npaws'],
    install_requires=reqs,
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)