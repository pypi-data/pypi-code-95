from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
   name='webscp',
   version='1.0.3.1',
   description='Scrape and email modules to an email id.',
   author='Govind Choudhary, Sreejith Subhash',
   author_email="govind2220000@gmail.com, sreejithsubhash198@gmail.com",
   long_description=long_description,   
   packages=find_packages(),  #same as name
   install_requires=['wheel', 
   'selenium==3.141.0',
   'Flask==2.0.1',
   'requests==2.22.0'], #external packages as dependencies
   python_requires='>=3',
   project_urls={
    'Documentation': 'https://github.com/govind2220000/image_scraper',
    'Source': 'https://github.com/govind2220000/image_scraper',
    'Tracker': 'https://github.com/govind2220000/image_scraper/issues',
},
)