import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-lib-flow.ci", # Replace with your own username
    version="1.21.6",
    author="Yang Guo",
    author_email="32008001@qq.com",
    description="flow.ci python open api lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flowci",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=3.6',
)