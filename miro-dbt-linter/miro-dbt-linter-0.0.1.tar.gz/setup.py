from setuptools import setup, find_packages
from miro_dbt_linter import __version__

setup(
    name='miro-dbt-linter',
    version=__version__,
    description='Extensible linter for dbt projects.',  
    author='Tom Waterman',
    author_email='tjwaterman99@gmail.com',
    url='https://github.com/tjwaterman99/miro-dbt-linter', 
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'lint=miro_dbt_linter.__main__:main'
        ]
    },
    install_requires=[
        'pydantic==1.8.2',
        'rich==10.9.0',
    ]
)