import setuptools

with open("README.md", "r") as desc_file:
    long_description = desc_file.read()

setuptools.setup(
    name="PyGL-Astroids",
    version="0.0.3",
    author="Zach Pierog",
    author_email="woldstn@live.com",
    description="Asteroids clone written using pyglet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Woldstn/PyGL-Astroids",
    project_urls={
        "Bug Tracker": "https://github.com/Woldstn/PyGL-Astroids/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['pyglet'],
    python_requires=">=3.6",
)