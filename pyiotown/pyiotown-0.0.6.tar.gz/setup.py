import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyiotown",
    version="0.0.6",
    author="boguen",
    author_email="boguen@coxlab.kr",
    description="IoT.own API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CoXlabInc/pyiotown",
    project_urls={
        "Bug Tracker": "https://github.com/CoXlabInc/pyiotown/issues",
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