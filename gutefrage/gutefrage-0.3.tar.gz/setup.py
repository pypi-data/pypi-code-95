from setuptools import setup
requires = [
    'beautifulsoup4>=4.9',
    'requests>=2.22',
]
long_desc = "# Unofficial Gutefrage API\n\nIt doesnt have a lot of features yet. Check it out [here](https://github.com/DAMcraft/gutefrage/wiki) how it works!"
setup(name='gutefrage',
      version='0.3',
      description='Unofficial GuteFrage api. Check https://github.com/DAMcraft/gutefrage/wiki on how to use it',
      url='https://github.com/DAMcraft/gutefrage',
      author='DAMcraft',
      author_email='',
      license='MIT',
      packages=['gutefrage'],
      zip_safe=False,
      install_requires=requires,
      long_description = long_desc,
      long_description_content_type = "text/markdown")