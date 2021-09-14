import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="habu-python-api",
    version="1.0.1",
    author="Habu",
    author_email="support@habu.com",
    description="Habu Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deklareddotcom/habu-api",
    project_urls={
        "Bug Tracker": "https://github.com/deklareddotcom/habu-api/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)