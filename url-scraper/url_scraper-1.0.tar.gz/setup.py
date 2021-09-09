from setuptools import setup

setup(
    name='url_scraper',
    version='1.0',    
    description='scrapes the weather page for urls',
    url='https://github.com/hjasmith1996/Project_2-v2.git',
    author='Harry Smith',
    author_email='hjasmith1996@gmail.com',
    license='BSD 2-clause',
    packages=['Project'],
    install_requires=['mpi4py>=2.0',
                      'numpy', 'selenium', 'pandas', 'beautifulsoup4', 'requests', 'sys'                    
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)