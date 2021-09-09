import setuptools

with open("README.md", "r", encoding="utf-8-sig") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.readlines()

setuptools.setup(
    name="roads-cba-py",
    version="0.1.1",
    author="Jamie Cook",
    author_email="jimi.cook@gmail.com",
    description="A pure python implementation of a CBA analysis for road maintenance prioritisation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vnopenroads/roads-cba-py",
    project_urls={
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['roads_cba_py'],
    python_requires=">=3.6",
    install_requires = requirements
)
