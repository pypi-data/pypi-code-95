from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='autobackuper',
    version='1.0.0',
    author="MaksL",
    author_email="contactmaksloboda@gmail.com",
    description="Automatic tool to backup a file to git",
    long_description_content_type="text/markdown",
    url="https://github.com/maksloboda/AutoBackuper",
    project_urls={
        "Bug Tracker": "https://github.com/maksloboda/AutoBackuper/issues",
    },
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    py_modules=['autobackuper'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'autobackuper = autobackuper:cli',
        ],
    },
    python_requires=">=3.6",
)
