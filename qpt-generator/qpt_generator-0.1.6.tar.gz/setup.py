import os

import pip

try:
    from Cython.Distutils.build_ext import new_build_ext
except ImportError:
    pip.main(['install', "cython"])
    from Cython.Distutils.build_ext import new_build_ext
from Cython.Build import cythonize

from setuptools import setup, find_packages, Extension
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

os.environ["CC"] = "g++"
os.environ["CXX"] = "g++"
extensions = [Extension("qpt_generator.qpt_generator",
                        sources=["qpt_generator/qpt_generator.pyx"],
                        language="c++",
                        extra_compile_args=["-std=c++11"],
                        extra_link_args=["-std=c++11"])]

setup(name="qpt_generator",
      version="0.1.6",
      description="Question Paper Template Generator",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="Niraj Kamdar",
      package_data={
          'qpt_generator': ["*.pxd", "*.pyx", "*.cpp", "*.h"]
      },
      packages=find_packages(),
      cmdclass={'build_ext': new_build_ext},
      ext_modules=cythonize(extensions, include_path=["qpt_generator"]),
      license='MIT',
      url='https://github.com/Niraj-Kamdar/qpt_generator',
      download_url='https://github.com/Niraj-Kamdar/qpt_generator/archive/master.zip',
      keywords=['question', 'paper', 'template', 'generator'],
      classifiers=[
          'Development Status :: 4 - Beta',
          # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          "Natural Language :: English",
          "Operating System :: OS Independent",
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      )
