version = "0.0.74"
install_requires = [
    "aiohttp>=3.6.2",
    "aiofiles>=0.4.0",
    "xlrd3>=1.1.0",
    "selenium>=3.141.0",
    "selenium-wire>=4.3.0",
    "twine>=3.4.1",
    "pyinstaller>=4.3",
    "chardet>=4.0.0",
]

from setuptools import setup, find_packages

setup(
    name = "beniutils",
    version = version,
    keywords="beni",
    description = "utils library for Beni",
    license = "MIT License",
    url = "https://pypi.org/project/beniutils/",
    author = "Beni",
    author_email = "benimang@126.com",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = install_requires,
    entry_points={
        "console_scripts": ["beniutils=beniutils.cmd:main"],
    },
)