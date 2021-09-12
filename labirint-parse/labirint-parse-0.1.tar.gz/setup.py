from setuptools import setup

setup(name='labirint-parse',
      version='0.1',
      description='Allows you to find out if a particular book is in stock and its price.',
      packages=['labirint_parser'],
      author_email='aleks.zhuravlev2002@mail.ru',
      entry_points='''
        [console_scripts]
        labirint_parser=labirint_parser.parser:main
    ''',
      zip_safe=False)