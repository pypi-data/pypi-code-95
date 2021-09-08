from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name='slite',
    version='0.0.2',
    description='Easily send data to Sqlite',
    long_description=readme,
    author='Dacker',
    author_email='hello@dacker.co',
    url='https://github.com/dacker-team/pysqlite',
    keywords='send data sqlite easy',
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires='>=3',
    install_requires=[
        "dbstream>=0.0.23"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
