from setuptools import setup, find_packages


setup(
    name="japick",
    version="0.3.1",
    packages=find_packages(),
    url="https://shodo.ink/",
    author="ZenProducts Inc.",
    author_email="info@shodo.ink",
    extras_require={
        "tests": ["pytest", "invoke", "black", "isort"],
    },
)
