from setuptools import setup

name = "types-xxhash"
description = "Typing stubs for xxhash"
long_description = '''
## Typing stubs for xxhash

This is a PEP 561 type stub package for the `xxhash` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `xxhash`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/xxhash. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `a1ca55037ad843e523bb6ae2e63a23414cf9ffac`.
'''.lstrip()

setup(name=name,
      version="2.0.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['xxhash-stubs'],
      package_data={'xxhash-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
