"""
stackvar
Copyright (c) 2021, Joaquin G. Duo

Code Licensed under MIT License. See LICENSE file.
"""
from setuptools import setup
import six

name = 'stackvar'

def long_description():
    with open('README') as f:
        if six.PY3:
            return f.read()
        else:
            return unicode(f.read())


setup(
  name = name,
  py_modules=[name],
  version = '1.3.0',
  description = 'Dispatch function\'s parameters through the callstack omitting arguments on intermediary functions. (a.k.a.: stack variable)',
  long_description=long_description(),
  long_description_content_type='text/x-rst',
  author = 'Joaquin Duo',
  author_email = 'joaduo@gmail.com',
  license='MIT',
  url = 'https://gitlab.com/joaduo/'+name,
  keywords = ['stack', 'callstack', 'variable', 'parameter'],
  install_requires=[],
)
