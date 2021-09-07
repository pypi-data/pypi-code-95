from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Download youtube music fast'
LONG_DESCRIPTION = 'pymymusic is a cli based youtube music downloader just type name of song hit enter and see the magic.'

#setup
setup(name='pymymusic',
version=VERSION,
description=DESCRIPTION,
long_description=LONG_DESCRIPTION,
url='https://github.com/unlikelycreator/pymynote',
author='iamhritikpawar',
author_email='hritikpawar.personal@gmail.com',
license='MIT',
packages=find_packages(),
install_requires=['youtube-search-python', 'youtube_dl', 'future', 'pyfiglet', 'jsons'],
zip_safe=False)