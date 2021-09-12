from setuptools import setup, find_packages
import codecs
import os

with open("README.md") as f:
    LONGDESCRIPTION = f.read()

VERSION = "0.9.5"
DESCRIPTION = "Async-Animanga, meant for Python. It scrapes the web for information about Manga, Anime and Doujin. (Hentai/Ecchi Anime not supported yet) It uses a modern Pythonic API and advanced aiohttp/asyncio implementations to provide extreme performance upgrades for large scale projects."

# Setting up
setup(
    name="Async-Animanga",
    version=VERSION,
    author="TheOnlyWayUp",
    author_email="thedarkdraconian@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONGDESCRIPTION,
    packages=find_packages(),
    install_requires=["bs4", "asyncio", "aiohttp", "html5lib"],
    keywords=["async", "aiohttp", "better_than_sync", "anime", "manga", "web scraping", "hentai", "doujin"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
