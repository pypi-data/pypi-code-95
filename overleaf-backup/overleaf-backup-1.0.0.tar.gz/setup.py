# coding: utf-8

"""
    Overleaf-Backup
    Tool to automatically backup your overleaf projects.

    The tool backups overleaf projects after a given time span.
    The time span and the overleaf project id's must be listed in the config file.
"""

from distutils.core import setup  # noqa: H301

NAME = "overleaf-backup"
VERSION = "1.0.0"
REQUIRES = [
    "requests",
]

setup(
    name=NAME,
    version=VERSION,
    packages=['overleaf_backup'],
    package_dir={'': 'src'},
    description="Overleaf projects backup tool",
    author="Philipp Baus",
    author_email="kontakt@philippbaus.de",
    url="https://github.com/BausPhi/overleaf-backup",
    license_files=('LICENSE',),
    keywords=["Overleaf", "Latex"],
    install_requires=REQUIRES,
    include_package_data=True,
    long_description="""
    Backup your self-hosted Overleaf projects
    """
)