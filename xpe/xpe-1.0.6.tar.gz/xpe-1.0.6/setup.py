from setuptools import setup

setup(
    name='xpe',
    version='1.0.6',
    author='github.com/charmparticle',
    packages=['xpe'],
    scripts=['bin/xpe'],
    url='https://github.com/charmparticle/xp',
    license='BSD 3-Clause License',
    description='A versatile commandline xpath parser',
    long_description=open('README.md').read(),
    install_requires=[
        "lxml",
        "chardet",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

