from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fast-keywords",
    version="0.1.0",
    description="Fast keyword identification with n-gram vector string matching.",
    license="unlicensed",
    url="https://github.com/christianj6/fast-keyword-identification",
    author="Christian Johnson",
    author_email="",
    package_dir={"fast-keywords": "fast_keywords"},
    packages=find_packages(),
    install_requires=[
        "pandas==1.2.3",
        "scikit-learn==0.23.0",
        "sparse-dot-topn==0.2.9",
        "dill==0.3.1.1",
        "nltk==3.4.5",
        "tqdm==4.47.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
