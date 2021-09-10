import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="memorywrap",
    version="1.1.0",
    author="La Rosa Biagio",
    author_email="larosa@diag.uniroma1.it",
    description="Memory Wrap: an extension for image classification models",
    install_requires=[
          'entmax',
          'torch>1.5'
      ],
      long_description=long_description,
   long_description_content_type="text/markdown",   packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
