from setuptools import setup, find_packages


setup(
    name='cxwidgets',
    version='0.13',
    author='Fedor Emanov',
    description='PyQt widgets connected to CX v4 control system framewok with designer plugins',

    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.5',
)