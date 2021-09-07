from setuptools import find_packages, setup

setup(
    name='digitalguide',
    packages=find_packages(),
    version='0.0.58',
    description='A Python Library to write digital guides for telegram',
    author='Soeren Etler',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)