from setuptools import setup

with open('README.md') as r: 
   for i in r:
    print(i)
setup(
    name='ip-locator-city',
    version='0.0.1',
    author='Clive Hunt',
    author_email='cliveapple265@gmail.com',
    description='ip locator with a simple ui',
    long_description='README.md',
    long_description_content_type='text/markdown',
    packages=['ip-locator-city'],
    package_dir={'ip-locator-city': 'src'},
    license='GPLv3',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        
    ],
    python_requires='>=3.0',
    
    package_data={
     
    },
)