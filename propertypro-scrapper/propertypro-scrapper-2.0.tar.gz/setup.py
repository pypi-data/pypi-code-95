from setuptools import setup, find_packages

 
classifiers = [
  'Intended Audience :: Education',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='propertypro-scrapper',
  version='2.0',
  description='A scraper that helps scrape a housing website propertypro',
  long_description=open('README.txt').read(),
  url='https://github.com/Ifyokoh/End-to-End-Machine-Learning',  
  author='Ifeoma Okoh',
  author_email='odibest1893@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='scraper', 
  packages=find_packages()
)
