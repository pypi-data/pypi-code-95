import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Comicsru",
    version="0.0.1",
    author="Cyb3rG0d",
    author_email="cyb3r-g0d.xrkbm@aleeas.com",
    description="A package to search and download comics on https://readcomicsonline.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CYB3R-G0D/Comicsru",
    project_urls={
        "Bug Tracker": "https://github.com/CYB3R-G0D/Comicsru/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=["Comicsru"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)