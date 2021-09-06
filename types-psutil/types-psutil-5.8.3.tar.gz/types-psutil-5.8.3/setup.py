from setuptools import setup

name = "types-psutil"
description = "Typing stubs for psutil"
long_description = '''
## Typing stubs for psutil

This is a PEP 561 type stub package for the `psutil` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `psutil`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/psutil. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `6188a3eec789b94cacd0c46e929321daad04b4b5`.
'''.lstrip()

setup(name=name,
      version="5.8.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['psutil-stubs'],
      package_data={'psutil-stubs': ['__init__.pyi', '_common.pyi', '_compat.pyi', '_psbsd.pyi', '_pslinux.pyi', '_psosx.pyi', '_psposix.pyi', '_psutil_linux.pyi', '_psutil_posix.pyi', '_psutil_windows.pyi', '_pswindows.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
