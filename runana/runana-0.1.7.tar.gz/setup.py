import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# VERSION = "0.1.5"

setup(
    name="runana",
    # version=VERSION,
    author="Jens Svensmark",
    author_email="jenssss@uec.ac.jp",
    version_config={
        "dev_template": "{tag}.dev{ccount}",
        # "dirty_template": "{tag}.dev{ccount}",
        # "dev_template": VERSION+".dev{ccount}",
        # "starting_version": VERSION,
        # "template": VERSION+"lol{tag}+dev{ccount}",
        },
    setup_requires=["setuptools-git-versioning"],
    # version_config={
    #     "template": "2021.{tag}",
    # },
    # setup_requires=["setuptools-git-versioning"],
    # description = ("An demonstration of how to create, document, and publish "
    #                                "to the cheese shop a5 pypi.org."),
    # license = "BSD",
    keywords="run analyse",
    # url = "http://packages.python.org/an_example_pypi_project",
    packages=['runana'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
    ],
)
