import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QAutoScrollLabel",
    version="1.0.4",
    author="Funkyo Enma",
    author_email="enmafunkyo@gmail.com",
    description="Auto scroll label for PyQt6",
    license= "GNU General Public License v3 or later (GPLv3+)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FunkyoEnma/QAutoScrollLabel",
    requieres=["PyQt6>=6.1.1",
               "multipledispatch>=0.6.0"],
    project_urls={
        "Bug Tracker": "https://github.com/FunkyoEnma/QAutoScrollLabel/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
