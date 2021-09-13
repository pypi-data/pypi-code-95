import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="everyworld",
    version="0.0.a1",
    author="AlexBroNikitin",
    author_email="alexnikitin071209@gmail.com",
    description="Collection of popular libraries and useful code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexbronikitin/everyworld",
    project_urls={
        "Bug Tracker": "https://github.com/alexbronikitin/everyworld/issues",
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