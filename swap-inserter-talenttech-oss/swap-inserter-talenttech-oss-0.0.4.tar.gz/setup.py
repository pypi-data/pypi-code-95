import os

from setuptools import setup, Command, find_packages


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./.pytest_cache ./.eggs')


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='swap-inserter-talenttech-oss',
    packages=find_packages(),
    version='0.0.4',
    license='MIT',
    description='Custom insert for script in vertica/ch',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dmitry Utiralov',
    author_email='d.utiralov@talenttech.ru',
    url='https://github.com/severgroup-tt/topmind-commons/tree/master/py/swap-inserter',
    install_requires=[
        'clickhouse-balanced-talenttech-oss==0.0.1',
        'vertica-connector-talenttech==1.2.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    cmdclass={
        'clean': CleanCommand
    }
)
