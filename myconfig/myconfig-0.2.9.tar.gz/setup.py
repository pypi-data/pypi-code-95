from pathlib import Path
from re import search

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("myconfig/__init__.py", encoding="utf-8") as f:
    version = search(r'__version__ = "(.*?)"', f.read()).group(1)

BASE_DIR = Path(__file__).parent
README = BASE_DIR.joinpath("README.md").read_text(encoding="utf-8")

setup(
    name="myconfig",
    version=version,
    description="Python Projects Configuration Manager",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/azureswastika/myconfig",
    download_url="https://github.com/azureswastika/myconfig/archive/{}.tar.gz".format(
        version
    ),
    author="Deni",
    license="MIT license",
    packages=["myconfig"],
    keywords=["myconfig", "config", "project config"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points={"console_scripts": ["myconfig = myconfig:main"]},
    install_requires=["PyYAML>=5.4.1", "toml>=0.10.2"],
    python_requires=">=3.6",
)
