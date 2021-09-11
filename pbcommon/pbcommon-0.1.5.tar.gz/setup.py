from setuptools import find_packages, setup

setup(
    name='pbcommon',
    packages=find_packages(),
    version='0.1.5',
    description='Piggy Bank Common Code',
    author='Hayden Smith',
    license='MIT',
    install_requires=['pytz==2021.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
    author_email='hayden.smith@gmail.com',
    url='https://github.com/pink-pigs/common',
    download_url='https://github.com/pink-pigs/common/archive/refs/tags/v0.1.5.tar.gz'
)
