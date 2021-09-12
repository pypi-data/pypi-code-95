from setuptools import setup, find_packages

VERSION = '0.0.3'
DESCRIPTION = 'Print with color easily and other cool stuff.'
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Setting up
setup(
    name="printutil",
    version=VERSION,
    author="Rambovic45",
    author_email="<author@mail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rambovic45/BetterPrints",
    project_urls={
        "Bug Tracker": "https://github.com/Rambovic45/BetterPrints/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
)