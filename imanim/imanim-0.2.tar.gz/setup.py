from setuptools import setup, find_packages

setup(
  name = 'imanim',
  packages=find_packages(),
  include_package_data=True,
  version = '0.2',
  description = 'show manim in jupyter',
  author = 'Kexin Zhang',
  author_email = 'zhangkx2@shanghaitech.edu.cn',
  license='MIT',
  keywords = ['computer science'],
  classifiers = [
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        ],
  install_requires=['manimlib'],
  entry_points={
    },

)
