from setuptools import setup

setup(
    name = 'vowelscounter',
    packages = ['VowelCounter'],
    include_package_data=True,  # muy importante para que se incluyan archivos sin extension .py
    version = '1.0',
    description = 'Vowel counter for given string',
    author='Oscar Batista',
    author_email="oscarjr01.13@gtmail.com",
    license="GPLv3",
    url="https://github.com/strymsg/python-simplemotds",
    classifiers = ["Programming Language :: Python :: 3", \
                   "License :: OSI Approved :: GNU General Public License v3 (GPLv3)", \
                   "Development Status :: 4 - Beta", "Intended Audience :: Developers", \
                   "Operating System :: OS Independent"],
)