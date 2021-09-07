import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = ["keyboard<=0.13.5"]

setuptools.setup(
    name="Menu-Creator",
    version="0.1.7",
    author="Golem_Iron",
    author_email="timulep@gmail.com",
    description="This module will allow you to quickly create interesting and user-friendly menus for console applications!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GolemIron/MenuCreator",
    project_urls={
        "Bug Tracker": "https://github.com/GolemIron/MenuCreator/issues",
    },
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    #package_dir={"": "src"},
    packages=setuptools.find_packages(),
    python_requires=">=3.7.9",
)