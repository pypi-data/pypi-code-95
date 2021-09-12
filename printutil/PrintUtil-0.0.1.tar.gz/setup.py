from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Print with color easily and other cool stuff.'

# Setting up
setup(
    name="PrintUtil",
    version=VERSION,
    author="Rambovic45",
    author_email="<author@mail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'print', 'util'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)