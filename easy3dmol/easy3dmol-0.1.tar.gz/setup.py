from setuptools import setup, find_packages

setup(
  name = 'easy3dmol',
  packages=find_packages(),
  include_package_data=True,
  version = '0.1',
  description = 'easier py3Dmol',
  author = 'Kexin Zhang',
  author_email = 'zhangkx2@shanghaitech.edu.cn',
  license='MIT',
  keywords = ['computational biology', 'chemical information',"protein"],
  classifiers = [
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        ],
  install_requires=[],
  entry_points={},

)