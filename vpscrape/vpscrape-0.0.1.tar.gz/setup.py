# -*- coding: utf-8 -*-
"""
Created on Sun Sep 12 21:59:18 2021

@author: forst
"""

from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='vpscrape',
  version='0.0.1',
  description='Web scraping based on selenium. supported for several website to do instantly webscraping with less code',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Vinson Phoan',
  author_email='contact@vinsonphoan.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='scrape, web scraping, news scraper, scraper', 
  packages=find_packages(),
  install_requires=['selenium==3.141.0'] 
)