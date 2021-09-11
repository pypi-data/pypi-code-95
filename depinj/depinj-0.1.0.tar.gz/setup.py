import setuptools

with open("Readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="depinj",
    version="0.1.0",
    author="Marcos Carrera",
    author_email="ramoscarrer@gmail.com",
    description="A friendly dependency injection package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rcmarc/depinj",
    project_urls={
        "Bug Tracker": "https://github.com/rcmarc/depinj/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
