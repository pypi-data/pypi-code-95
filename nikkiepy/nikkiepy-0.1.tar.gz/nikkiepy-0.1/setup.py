import setuptools
import setuptools

with open("README.md", 'r', encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nikkiepy",
    version="0.1",
    author="NikkieDev#6322",
    author_email="nikkieschaad@gmail.com",
    description="Custom python library by: NikkieDev",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NikkieCodes/nikkiepy",
    package_dir={"": "nikkiepy"},
    python_requires=">=3.7",
    packages=setuptools.find_packages(where="nikkiepy")
)