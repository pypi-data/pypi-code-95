import setuptools

setuptools.setup(
    name="harveyutils",
    version="1.1.4",
    long_description="Harvey Utls",
    packages=["harveyutils"],
    license="MIT",
)

# python setup.py sdist
# twine upload --skip-existing dist/*
# twine upload dist/*