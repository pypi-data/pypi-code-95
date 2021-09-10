from setuptools import setup

setup(
    name = "patcat",
    version = "2021.09.10",
    description = "Outputs text with rainbow colors.",
    long_description = open("readme.md").read(),
    long_description_content_type = "text/markdown",
    url = "https://gitdab.com/endie2/pat",
    author = "Lavender Perry",
    author_email = "endie2@protonmail.com",
    packages = ["pat"],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities"
    ]
)
