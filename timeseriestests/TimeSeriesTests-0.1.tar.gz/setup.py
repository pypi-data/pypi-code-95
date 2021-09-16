from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(
  name = 'TimeSeriesTests',         
  packages = ['timeseriestests'],   
  version = '0.1',      
  license="MIT",        
  long_description_content_type="text/markdown",
  long_description= readme(),
  description = 'Simple time series tests normality, stationarity, integration and causality tests',  
  author = 'junhyuck song',                   
  author_email = 'junhyuck.song@gmail.com',      
  url = 'https://github.com/Jsong1836/Time-series-tests',   
  download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',    
  keywords = ['timeseries', 'stationarity'],   
  install_requires=[            
          'numpy',
          'pandas',
          'arch', 
          'scipy'],
  classifiers=[
          'Environment :: Win32 (MS Windows)',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
      ], )