import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pdcompare",
    version="0.1.2",
    author="Jace Iverson",
    author_email="iverson.jace@gmail.com",
    description="Used to compare 2 Pandas DFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaceiverson/pandas-compare",
    project_urls={
        "Bug Tracker": "https://github.com/jaceiverson/pandas-compare",
    },
    packages = ['pdcompare'
            ]

)