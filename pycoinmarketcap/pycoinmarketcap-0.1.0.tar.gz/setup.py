from setuptools import setup, find_packages
import pathlib

README = (pathlib.Path(__file__).parent / "README.md").read_text()

setup(
    name="pycoinmarketcap",
    version="0.1.0",
    description="A simple api wrapper for the CoinMarketCap API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/World-of-Cryptopups/pycoinmarketcap",
    author="TheBoringDude",
    author_email="iamcoderx@gmail.com",
    license="ISC",
    project_urls={
        "Bug Tracker": "https://github.com/World-of-Cryptopups/pycoinmarketcap/issues"
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["examples"]),
    include_package_data=True,
    install_requires=["requests"],
)
