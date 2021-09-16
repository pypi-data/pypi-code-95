from setuptools import setup
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="tablespoon",
    version="0.1.0",
    license="UNLICENSE MIT",
    description="Time-series benchmarks methods that are Simple and Probabilistic",
    author="alexhallam",
    author_email="alexhallam6.28@gmail.com",
    url="https://github.com/alexhallam/tablespoon",
    download_url="https://github.com/alexhallam/tablespoon/releases/tag/0.1.0",
    keywords=["forecasting", "forecast", "probabilistic", "naive", "benchmark", "seasonal naive", "mean forecast"],
    py_modules=["forecasters"],
    install_requires=["pandas", "numpy", 'cmdstanpy', 'pkg_resources'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.9",
    ],
)
