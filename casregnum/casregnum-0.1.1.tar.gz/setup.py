import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fileVersion:
    version_number = fileVersion.readline().strip()

setuptools.setup(
    name="casregnum",
    version=version_number,
    description="casregnum provides a Python class 'CAS' for working with CAS Registry Numbers®. It allows managing, sorting and checking CAS numbers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Axel Müller",
    author_email="molshape@gmx.net",
    maintainer="molshape",
    maintainer_email="molshape@gmx.net",
    url="https://github.com/molshape/casregnum",
    project_urls={
        "Bug Tracker": "https://github.com/molshape/casregnum/issues",
    },
    license="LICENSE",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    package_dir={"": "src"},
    py_modules=["casregnum"],
    include_package_data=True,
    python_requires=">=3.7",
)
