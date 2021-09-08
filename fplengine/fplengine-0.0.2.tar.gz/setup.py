from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='fplengine',
    version='0.0.2',
    description='Package to pull fantasy football data and run your account',
    long_description=long_description,
    url='https://github.com/HendoGit/FantasyFootyBot.git',
    author='Alex Henderson',
    license='Apache',
    packages=find_packages(),
    install_requires=['requests', 'sqlalchemy', 'psycopg2', 'pandas']
)