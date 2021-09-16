from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 3 - Alpha',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
  'Programming Language :: Python :: 3'
]

setup(
    name='asciiconv',
    version='0.2.2',
    description='Convert text to be ASCII compatiable and back',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='',  
    author='Synergetic00',
    license='GPLv3', 
    classifiers=classifiers,
    keywords='ascii', 
    packages=find_packages(),
    install_requires=[''] 
)