"""Setup for package."""
import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
VERSION = "0.0.38"

setup(
    name="apgw",
    version=VERSION,
    description=(
        "A simple wrapper around asyncpg to make some common actions simpler."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Trey Cucco",
    author_email="fcucco@gmail.com",
    url="https://gitlab.com/tcucco/apgw",
    download_url="https://gitlab.com/tcucco/apgw/-/archive/master/apgw-master.tar.gz",
    package_data={"apgw": ["py.typed"]},
    packages=["apgw"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
    license="MIT",
    platforms="any",
    zip_safe=False,
    install_requires=[
        "asyncpg",
    ],
)
