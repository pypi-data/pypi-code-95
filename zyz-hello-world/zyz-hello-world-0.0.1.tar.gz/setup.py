from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zyz-hello-world',
    version='0.0.1',
    packages=find_packages(),
    url='https://github.com/pypa/sampleproject',
    license='MIT',
    author='Yizhe Zeng',
    author_email='author@example.com',
    description='A small example package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
