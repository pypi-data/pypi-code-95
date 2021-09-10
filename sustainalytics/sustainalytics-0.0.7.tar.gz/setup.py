import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name = "sustainalytics",
    version = "0.0.7",
    description ="This is a package that helps clients access sustainalytics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author = "Kienka Cromwell Kio",

    url='https://github.com/Kienka/sustainalytics',
    author_email = "kienka.kio@sustainalytics.com",
    packages = setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=['pandas','requests','tqdm']
)