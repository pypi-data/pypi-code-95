import os
from setuptools import setup, find_packages

EXTRAS_REQUIRE = {
    "pdfs": ["pdf-annotate", "pdf2image"]
}
def read(rel_path):
    """Read lines from given file"""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()

def get_version(rel_path):
    """Read __version__ from given file"""
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError(f"Unable to find a valid __version__ string in {rel_path}.")

setup(
    name='jsonshower',
    version=get_version("jsonshower/__init__.py"),
    url='https://github.com/RelevanceAI/jsonviewer',
    author='Jacky Wong',
    author_email='jacky.wong@vctr.ai',
    description='Json Viewer with additional multimedia and highlighting support',
    packages=find_packages(),
    install_requires=['pandas', 'fuzzysearch'],
    extras_require=EXTRAS_REQUIRE
)
