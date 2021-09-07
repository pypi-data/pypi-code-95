from setuptools import setup
from truedata_ws import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='truedata_ws',
    version=__version__,
    packages=['truedata_ws', 'truedata_ws.websocket'],
    url='https://github.com/kapilmar/truedata-ws',
    # license='GNU General Public License v3 (GPLv3)',
    author='Kapil Marwaha',
    author_email='kapil@truedata.in',
    description="Truedata's Official Python Package",
    install_requires=requirements,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
