from setuptools import setup, find_packages

setup(
   name='webscp',
   version='1.0.1',
   description='Scrape and email modules to an email id.',
   author='Govind Choudhary <govind2220000@gmail.com>, Sreejith Subhash <sreejithsubhash198@gmail.com>',
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