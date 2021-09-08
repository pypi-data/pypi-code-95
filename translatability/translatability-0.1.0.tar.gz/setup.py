from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="translatability",
    version="0.1.0",
    description="Score German noun compounds according to their English-translatability.",
    url="https://github.com/christianj6/assessing-translatability",
    author="Christian Johnson",
    author_email="",
    license="unlicensed",
    package_dir={"translatability": "translatability"},
    packages=find_packages(),
    install_requires=[
        "nltk==3.6.2",
        "beautifulsoup4==4.9.3",
        "pyspellchecker==0.6.2",
        "deep-translator==1.5.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
