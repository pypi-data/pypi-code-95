import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dq_whistler",                     # This is the name of the package
    version="0.0.1-alpha.1",                        # The initial release version
    author="Naresh Kumar",                     # Full name of the author
    author_email='nareshbabral@gmail.com',
    description="A comprehensive library for data quality checks",
    url="https://github.com/nareshbab/dq_whistler",
    download_url="https://github.com/nareshbab/dq_whistler/archive/refs/tags/v0.0.1-alpha.tar.gz",
    license='MIT',
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',     # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["dq_whistler"],             # Name of the python package
    install_requires=[
        "pyspark"
    ]
)
