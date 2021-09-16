from bs4 import BeautifulSoup
import os,sys
import subprocess
def install(moudle=None,index='https://pypi.tuna.tsinghua.edu.cn/simple'):
    pip_path=''

    for i in sys.executable.split('\\')[:-1]:
        pip_path += i + '\\'
    pip_path += 'Scripts\\pip.exe'
    command = f'{sys.executable} {pip_path} install {moudle} -i {index}'
    with open('install.bat','w') as f:
        f.write('@echo off\n'+command)
    subprocess.call('install.bat')
def uninstall(moudle=None):
    pip_path = ''

    for i in sys.executable.split('\\')[:-1]:
        pip_path += i + '\\'
    pip_path += 'Scripts\\pip.exe'
    command = f'{sys.executable} {pip_path} uninstall {moudle}'
    with open('uninstall.bat','w') as f:
        f.write('@echo off\n'+command)
    subprocess.call('uninstall.bat')

if __name__ == '__main__':
    print(install('pip'))