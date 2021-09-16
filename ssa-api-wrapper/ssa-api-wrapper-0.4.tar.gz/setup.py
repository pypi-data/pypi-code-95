import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()



setuptools.setup(
    name="ssa-api-wrapper",
    version="0.4",
    author="Phoneguytech75",
    description="Wrapper for SSA API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Phoneguytech75/SSA-API-WRAPPER",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["requests"],
)
