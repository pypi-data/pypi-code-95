# coding: utf-8
'''
Informações sobre o pacote
'''

#
# Dependencies
#
from setuptools import setup

#
# Link to README.md file
#
with open (
    file="README.md"
,   mode="r"
,   encoding="utf8"
) as fh:
    readme = fh.read()

#
# Setup
#
setup (
    name='almaviva'
,   version='1.1.0'
,   url='https://github.com/Almaviva-do-Brasil/almaviva'
,   packages=[
        'almaviva/database'
    ,   'almaviva/file'
    ,   'almaviva/ihm'
    ,   'almaviva/logging'
    ,   'almaviva/webdriver'
    ]
,   install_requires=[
        'pyodbc'
    ,   'wmi'
    ,   'selenium'
    ]
,   author='Assad, Felipe'
,   author_email='fassad@almavivadobrasil.com.br'
,   description=u'Biblioteca com funções personalizadas desenvolvidos para Almaviva Do Brasil'
,   license='Almaviva do Brasil Licence'
,   keywords='almavivadobrasil, database, logging, file, ihm, webdriver'
,   long_description=readme
,   long_description_content_type="text/markdown"
)