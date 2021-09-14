import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="icloudbypass-awesomekid",
    version="0.0.1",
    author="AwesomeKid",
    author_email="rohanshri66@gmail.com",
    description="The one and only, iCloud bypass! [setup.py version]",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://therickroll.com",
    project_urls={
        "Bug Tracker": "https://therickroll.com",
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
