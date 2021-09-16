
from distutils.core import setup
setup(
  name = 'YOMAPI',
  packages = ['YOMAPI'],
  version = '0.0.14',
  license='MIT',
  description = 'A PACKAGE TO USE THE SAME YOM API INTERFACE FROM YOM INTEGRATIONS',
  author = 'Camilo Jiménez',
  author_email = 'camilo@youorder.me',
  url = 'https://github.com/user/reponame',
  # download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz', 
  keywords = ['YOM-INTEGRATIONS'],   # Keywords that define your package best
  install_requires=[
    'requests'
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
  python_requires='>=3.6',
)