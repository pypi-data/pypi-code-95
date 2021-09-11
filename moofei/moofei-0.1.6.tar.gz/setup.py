# -*- coding: utf-8

import os
#from setuptools import setup,Extension
from distutils.core import setup, Extension
from distutils.sysconfig import get_python_lib

install_requires  = [ # "Cython"
        "chardet", 
    ]
requirements = install_requires    
long_description=open('README.md').read()
long_description_content_type="text/x-rst" 
   
setup(
    name = 'moofei',  # 
    version = '0.1.6',  # 
    description = "find,valid,tree,date,db,waf By mufei",
    long_description_content_type = long_description_content_type,
    long_description = long_description,
    
    author = 'mufei', # maintainer="None",  # 
    author_email = 'ypdh@qq.com', # maintainer_email="None",  # 
    url = "http://www.mufei.ltd",  # 
    download_url = "",  # 
    keywords = "moofei mufei find valid tree date db waf",
    #py_modules=['package'],  # 
    
    packages   = ['moofei','moofei.tests','moofei.find','moofei.valid','moofei.ext'],          # 
    package_dir= {"moofei": "lib/moofei"},
    
    ext_modules = [Extension('moofei._find',['src/_find.c']), 
                   Extension('moofei._path',['src/_path.c']), 
                   Extension('moofei._ftp',['src/_ftp.c']),
                   Extension('moofei._valid',['src/_valid.c']),
                   Extension('moofei._db',['src/_db.c']),
                   ],
    requires = install_requires,
    install_requires = install_requires, #auto install
    setup_requires = install_requires, #list show
    
    zip_safe = True,
    include_package_data = True, #
    
    package_data={"moofei": ["templates/*.html", "static/*.html", "static/*.js", "static/*.ico"]}, #moofei path
    #data_files={"moofei": ["lib/moofei/static/*.html"]}, #system path
           
    python_requires = ">=2.6, !=3.0.*, !=3.1.*, !=3.2.*",  #  
    license = "BSD",
    #extras_require={
    #    'PIL':  ["PIL",],
    #}
    
)

