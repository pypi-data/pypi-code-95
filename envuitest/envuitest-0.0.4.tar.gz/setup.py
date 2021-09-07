import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="envuitest",
    version="0.0.4",
    author="Even Lan",
    author_email="goeasyway@163.com",
    description="Web Auto Test Framework with Selenium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goeasyway/EasyPlug",
    project_urls={
        "Bug Tracker": "https://github.com/goeasyway/EasyPlug/issues",
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