import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Environment :: Win32 (MS Windows)",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: OS Independent",
    "Topic :: Internet",
    "Topic :: Terminals",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
]
    
setuptools.setup(
    name="bayscrape",
    version="1.1.3",
    setup_requires=["flake8"],
    install_requires=[
        "requests>=2.24.0",
        "beautifulsoup4>=4.9.3",
        "colored>=1.4.2",
        "setuptools>=50.3.2",
        "beautifultable>=1.0.0",
    ],
    url="https://github.com/mattshu/bayscrape",
    license="GNU GPLv3",
    author="Matt Kelley",
    author_email="mattshu32@gmail.com",
    description="Safely browse legal torrents from the comfort of your command-line.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    packages=setuptools.find_packages(exclude=['test']),
    include_package_data=True,
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "bayscrape=bayscrape.__main__:main",
            ]
    },
)
