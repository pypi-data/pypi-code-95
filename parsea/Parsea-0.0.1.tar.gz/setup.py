import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Parsea",
    version="0.0.1",
    py_modules=["Parsea"],
    author="Xp",
    author_email="breakdowneternity@gmail.com",
    description="Simple Scannerless Parser library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xp-op/Parsea",
    project_urls={
        "Bug Tracker": "https://github.com/Xp-op/Parsea/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={'':'Parsea'},
    python_requires=">=3.6",
)