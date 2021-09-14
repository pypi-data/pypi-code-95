from setuptools import find_packages, setup

README = "README.md"

with open(README, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mspell",
    version="0.0.1",
    author="Malcolm Sailor",
    author_email="malcolm.sailor@gmail.com",
    description="Spell musical pitches",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["numpy"],
    url="https://github.com/malcolmsailor/mspell",
    project_urls={
        "Bug Tracker": "https://github.com/malcolmsailor/mspell/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
)
