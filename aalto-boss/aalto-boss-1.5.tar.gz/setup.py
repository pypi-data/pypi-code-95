import re
from os import path

from setuptools import find_packages, setup


def parse_metadata(
    file_path, extra_keywords=None, add_dunder=True, find_author_list=False
):
    """Parse core Python package metadata stored in a file. """

    metadata = {}
    if extra_keywords:
        metadata.update({k: None for k in extra_keywords})
    metadata.update(
        {
            "version": None,
            "url": None,
            "author": None,
            "author_email": None,
            "maintainer": None,
            "maintainer_email": None,
            "license": None,
            "description": None,
        }
    )

    with open(file_path) as fd:
        text = fd.read()

    # The following regex will match the contents of any non-multiline string.
    # Note: Surrounding quotes are NOT included.
    re_str_tmpl = "{}\s*=\s*['\"](.*)['\"]"

    for key in metadata.keys():
        if add_dunder:
            var_name = "__{}__".format(key)
        else:
            var_name = key
        match = re.search(re_str_tmpl.format(var_name), text)
        if match:
            metadata[key] = match.group(1)

    # Extra: If no author was found, look for a python list named authors or _authors__
    # and use it to build the author string.
    if find_author_list and not metadata["author"]:
        match = re.search("__authors__\s*=\s*[\[\(](.*)[\)\]]", text, re.DOTALL)
        if match:
            stringified_list = match.group(1)
            author_list = stringified_list.split(",")
            author_list = [auth.strip()[1:-1] for auth in author_list]
            metadata["author"] = ", ".join(author_list)

    metadata = {k: v for k, v in metadata.items() if v is not None}
    return metadata


metadata = parse_metadata("boss/__init__.py", find_author_list=True)

with open("README.rst", encoding="utf-8") as f:
    long_description = f.read()

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "License :: OSI Approved :: Apache Software License",
]

setup(
    name="aalto-boss",
    version=metadata["version"],
    url=metadata["url"],
    author=metadata["author"],
    maintainer=metadata["maintainer"],
    maintainer_email=metadata["maintainer_email"],
    description=metadata["description"],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license=metadata["license"],
    include_package_data=True,
    classifiers=classifiers,
    packages=find_packages(),
    install_requires=["GPy", "matplotlib>=3.0"],
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "boss=boss.__main__:main",
        ],
    },
)
