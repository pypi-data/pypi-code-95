from setuptools import find_packages, setup

setup(
    name="nist80022",
    version="0.1.0",
    license="MIT",
    description="Library for implementing NIST 800-22 testsuite.",
    packages=find_packages(),
    maintainer="Chris Gravel",
    maintainer_email="cpagravel@gmail.com",
    url = "https://github.com/cpagravel/randomness_testsuite",
    download_url = "https://github.com/cpagravel/randomness_testsuite/archive/0.1.0.tar.gz",
    keywords = ["Randomness", "NIST Test Suite", "SP80022", "NIST 800-22"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=["numpy", "scipy"],
)
