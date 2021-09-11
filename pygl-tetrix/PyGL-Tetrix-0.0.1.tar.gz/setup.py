import setuptools

with open("README.md", "r") as desc_file:
    long_description = desc_file.read()

setuptools.setup(
    name="PyGL-Tetrix",
    version="0.0.1",
    author="Zach Pierog",
    author_email="woldstn@live.com",
    description="One-day Tetris programming challenge using pyglet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Woldstn/PyGL-Tetrix",
    project_urls={
        "Bug Tracker": "https://github.com/Woldstn/PyGL-Tetrix/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)