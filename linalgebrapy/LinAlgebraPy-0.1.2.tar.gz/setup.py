from setuptools import _install_setup_requires, find_packages, setup

setup(
    name='LinAlgebraPy',
    packages=find_packages(),
    version='0.1.2',
    description='Linear Algebra Package',
    long_description="This is a Linear Algebra Package \n Easy to use with simple methods for calculation and\n the float precision is set to -13 for better precision      \n PS: Don't use version 0.1.1, it contains errors",
    author='Rami El Dahouk',
    author_email="ramipypi@outlook.com",
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='test',
    python_requires=">=3.0",
)