from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'The elementary python pattern programs'

# Setting up
setup(
    name="pypatt",
    version=VERSION,
    author="k__rushi2.x.0 (Rushikesh Kundkar)",
    author_email="<r4002001005025k@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'pattern programming','elementary programs'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)