import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QAutoScrollLabel",
    version="1.0.31",
    author="Funkyo Enma",
    author_email="enmafunkyo@gmail.com",
    description="Auto scroll label for PyQt6",
    long_description=long_description,
    script_name="AutoScroll.py",
    long_description_content_type="text/markdown",
    url="https://github.com/FunkyoEnma/QAutoScrollLabel",
    project_urls={
        "Bug Tracker": "https://github.com/FunkyoEnma/QAutoScrollLabel/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ]
)
