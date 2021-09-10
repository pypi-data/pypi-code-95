import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="quickhtml",
    version="2.0.3",
    author="ckc-dev",
    author_email="ckc-dev@pm.me",
    description="A simple Markdown to HTML preprocessor that doesn't require third-party modules.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ckc-dev/QuickHTML",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
