import os

from setuptools import setup, find_packages

PROJECT_NAME = 'kkba'
PACKAGE_NAME = 'kkba'

here = os.path.abspath(os.path.dirname(__file__))
project_info = {
    "name":
        "kkba",
    "version":
        "0.8.14",
    "author":
        "dylan",
    "author_email":
        "shddylan@163.com",
    "url":
        "https://github.com/haidongsong/kkba",
    "license":
        "MIT",
    "classifiers": [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    'requires': ['pyperclip>=1.8.0', 'rich>=9.13.0', 'requests'],
    "description":
        "A Library to Convert Curl to Python Requests File",
    "console_scripts": ["kkba = kkba.__main__:main"]
}

try:
    README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()
except:
    README = ""

setup(name=project_info['name'],
      version=project_info['version'],
      author=project_info['author'],
      author_email=project_info['author_email'],
      url=project_info['url'],
      # license=project_info['license'],
      description=project_info['description'],
      # classifiers=project_info['classifiers'],
      long_description=README,
      long_description_content_type="text/markdown",
      packages=find_packages('src'),
      # packages=find_packages(),
      # zip_sage=False,
      include_package_data=True,  # 打包包含静态文件标识
      package_dir={'': 'src'},
      install_requires=project_info['requires'],
      platforms='any',
      zip_safe=True,
      keywords='curl pypi',
      entry_points={'console_scripts': project_info['console_scripts']},
      python_requires=">=3.6"

      )
