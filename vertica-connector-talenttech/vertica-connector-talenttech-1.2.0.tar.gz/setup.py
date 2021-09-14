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
    name='vertica-connector-talenttech',
    packages=find_packages(),
    version='1.2.0',
    license='MIT',
    description='TopMind Vertica Connector Wrapper',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Dmitry Utiralov',
    author_email='d.utiralov@talenttech.ru',
    url='https://github.com/severgroup-tt/topmind-commons/py/vertica-connector',
    install_requires=[
        'vertica_python'
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
