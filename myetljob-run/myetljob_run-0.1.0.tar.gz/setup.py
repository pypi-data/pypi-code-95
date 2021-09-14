from setuptools import find_packages, setup

setup(
    name='myetljob_run',
    packages=find_packages(include=['tg_etl_lib']),
    version='0.1.0',
    description='My first ETL library',
    author='ygng',
    license='MIT',
    install_requires=['findspark', 'pyspark', 'delta-spark'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)