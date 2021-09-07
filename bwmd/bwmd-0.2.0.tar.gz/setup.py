from setuptools import setup, find_packages
# from pybind11.setup_helpers import Pybind11Extension, build_ext

with open("README.md", "r") as f:
    long_description = f.read()


# ext_modules = [
#     Pybind11Extension(
#         "bwmd_utils",
#         ["src/bwmd_utils.cpp"],
#     )
# ]


setup(
    name="bwmd",
    version="0.2.0",
    description="Fast text similarity with binary encoded word embeddings.",
    url="https://github.com/christianj6/binarized-word-movers-distance.git",
    author="Christian Johnson",
    author_email="",
    license="unlicensed",
    package_dir={"bwmd": "bwmd"},
    packages=find_packages(),
    install_requires=[
        "tensorflow==2.6.0",
        "tensorflow_probability==0.13.0",
        "numpy==1.19.5",
        "tqdm==4.61.2",
        "scipy==1.7.1",
        "nltk==3.6.2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    # ext_modules=ext_modules,
    # cmdclass={"build_ext": build_ext},
    long_description=long_description,
    long_description_content_type="text/markdown",
)
