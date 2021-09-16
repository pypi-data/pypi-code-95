import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="BlastPY",
    version="1.0.1",
    author="W̷̛͒i̶̓͗l̷͗̌ľ̶͘",
    author_email="epicugric@gmail.com",
    description="a machine learning framework by W̷̛͒i̶̓͗l̷͗̌ľ̶͘",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ugric/Blast",
    project_urls={
        "Bug Tracker": "https://github.com/Ugric/Blast/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "BlastPY"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
