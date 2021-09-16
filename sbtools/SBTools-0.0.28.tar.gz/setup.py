#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: Marj
# Mail: 598175639@qq.com
# Created Time:  2019-09-05 16:36:34
#############################################

from setuptools import setup, find_packages
import requests
from bs4 import BeautifulSoup

def get_html():
    url='https://pypi.org/project/SBTools/'
    r=requests.get(url)
    return r.text

soup = BeautifulSoup(get_html(), 'html.parser')
sb_ver_list=soup.find_all(name='h1',attrs={"class":"package-header__name"})[0].text.strip().replace("SBTools","").split(".")
sb_ver_list[-1]=int(sb_ver_list[-1])+1
sb_version=""
for i in sb_ver_list:
    if sb_version=="":
        sb_version=str(i)
    else:
        sb_version=sb_version+"."+str(i)
print(sb_version)

setup(
    name = "SBTools",
    version = sb_version, 
    keywords = ("pip", "SBTools","sbtools"),
    description = "工具箱",
    long_description = "懒人工具箱",
    license = "MIT Licence",

    url = "",
    author = "Marj",
    author_email = "598175639@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests","pymysql"]
)