#!/usr/bin/env python
# coding: utf-8

"""The script supports publishing the mkdocs-boring-theme to PyPI.

Instructions to release a new version:

    (1) Prepare the release

    * Change the version number in setup.py
    * Call:

        $ python setup.py prepare


    (2) Push to PyPI

    This step releases the new version of the software.
    Ensure the credentials are in pypirc.

    * Call:

        $ python setup.py publish

    (3) Post publish

    * Update the information on the project's home page
"""

# standard lib
import os
import setuptools
import sys

# first party
import boring_theme


VERSION = '0.1.11'

FILE_ENCODING = "utf-8"
README_PATH_IN = "docs/index.md"
README_PATH_OUT = "README.md"
RELEASE_NOTES = "docs/releases.md"
LICENSE_PATH = "LICENSE"

CLASSIFIERS = [
        "Development Status :: 3 - alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
]


def _read(path: str) -> str:
    """Reads a text file and returns the content as unicode string.
    :param path: File path
    :return: content
    """
    with open(path, "rb") as f:
        b = f.read()
    return b.decode(FILE_ENCODING)


def _write(content: str, path: str):
    """Writes some content to a file
    :param content: Content of the new file
    :param path: File path
    """
    with open(path, "wb") as f:
        b = content.encode(FILE_ENCODING)
        f.write(b)


def _build_long_descr() -> str:
    """Build the long description
    :return: long description
    """
    readme = _read(README_PATH_IN)
    release_notes = _read(RELEASE_NOTES)
    license = """\
# License

""" + _read(
        LICENSE_PATH
    )

    description = "\n\n".join([readme, license])

    return description


def prepare():
    """Prepares the process of publishing the new package."""
    # Write long description to README_PATH_OUT
    descr = _build_long_descr()
    _write(descr, README_PATH_OUT)


def publish():
    """Automates the process of publishing the new package."""

    if os.path.isdir("./dist"):
        os.system("rm -R ./dist")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")


#
#
# Setup content
#
#


def main(args):
    command = args[-1]

    if command == "publish":
        publish()
        sys.exit()
    elif command == "prepare":
        prepare()
        sys.exit()

    descr = _read(README_PATH_OUT)

    setuptools.setup(
        name="mkdocs-boring-theme",
        version=VERSION,
        url='https://resing.dev/mkdocs-boring-theme/',
        license='MIT',
        description='Boring MkDocs theme based on CSS framework Min (mincss.com)',
        long_description=descr,
        long_description_content_type="text/markdown",
        author='Max Resing',
        author_email='max.resing@protonmail.com',
        packages=setuptools.find_packages(),
        include_package_data=True,
        install_requires=['mkdocs>=1.1'],
        python_requires='>=3.7',
        entry_points={
            'mkdocs.themes': [
                'boring = boring_theme',
            ]
        },
        project_urls={
            "Source": "https://codeberg.org/resingm/mkdocs-boring-theme",
            "Tracker": "https://codeberg.org/resingm/mkdocs-boring-theme/issues",
        },
        zip_safe=False,
    )


if __name__ == "__main__":
    main(sys.argv)

