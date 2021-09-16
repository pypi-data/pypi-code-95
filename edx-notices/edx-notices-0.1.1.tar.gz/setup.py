#!/usr/bin/env python
"""
Package metadata for notices.
"""
import os
import re
import sys

from setuptools import setup


def get_version(*file_paths):
    """
    Extract the version string from the file.

    Input:
     - file_paths: relative path fragments to file with
                   version string
    """
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(filename, encoding="utf8") as version_file:
        version_file_contents = version_file.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file_contents, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def load_requirements(*requirements_paths):
    """
    Load all requirements from the specified requirements files.

    Returns:
        list: Requirements file relative path strings
    """
    requirements = set()
    for path in requirements_paths:
        with open(path, encoding="utf8") as req_file:
            requirements.update(
                line.split("#")[0].strip() for line in req_file.readlines() if is_requirement(line.strip())
            )
    return list(requirements)


def is_requirement(line):
    """
    Return True if the requirement line is a package requirement.

    Returns:
        bool: True if the line is not blank, a comment, a URL, or
              an included file
    """
    return line and not line.startswith(("-r", "#", "-e", "git+", "-c"))


VERSION = get_version("notices", "__init__.py")

if sys.argv[-1] == "tag":
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    os.system("git push --tags")
    sys.exit()

with open(os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf8") as readme_file:
    README = readme_file.read()
with open(os.path.join(os.path.dirname(__file__), "CHANGELOG.rst"), encoding="utf8") as changelog_file:
    CHANGELOG = changelog_file.read()

setup(
    name="edx-notices",
    version=VERSION,
    description="""An edx-platform plugin which manages notices that must be acknowledged""",
    long_description=README + "\n\n" + CHANGELOG,
    author="edX",
    author_email="mtuchfarber@edx.org",
    url="https://github.com/edx/platform-plugin-notices",
    packages=[
        "notices",
    ],
    include_package_data=True,
    install_requires=load_requirements("requirements/base.in"),
    python_requires=">=3.8",
    license="AGPL 3.0",
    zip_safe=False,
    keywords="Python edx",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "lms.djangoapp": [
            "notices = notices.apps:NoticesConfig",
        ],
    },
)
