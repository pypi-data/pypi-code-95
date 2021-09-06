"""
https://packaging.python.org/tutorials/packaging-projects/
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="latest-indonesia-earthquake",
    version="0.1",
    author="Ade Ristanto",
    author_email="ade.ristanto@gmail.com",
    description="Latest information Indonesia earthquake from Meteorological, Climatological, and Geophysical Agency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ade-Project/latest-indonesia-earthquake",
    project_urls={
        "GitHub": "https://github.com/AdeRistanto",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable"
    ],
    # package_dir={"": "src"},
    # packages=setuptools.find_packages(where="src"),
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)

