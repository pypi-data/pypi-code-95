from setuptools import setup

classifiers = """
Topic :: Multimedia :: Sound/Audio
Programming Language :: Python :: 2
Programming Language :: Python :: 3
"""

setup(name='ctcsound',
      version='6.17b1',
      url='https://github.com/fggp/ctcsound',
      description='Python bindings to the Csound API using ctypes', 
      classifiers=filter(None, classifiers.split('\n')),
      author='Francois Pinot',
      py_modules=['ctcsound'],
      install_requires=[
        'numpy>=1.16'
      ]
)


