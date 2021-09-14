from bs4 import BeautifulSoup
import os,sys
def install(moudle=None,index='https://pypi.tuna.tsinghua.edu.cn/simple'):
    pip_path=''

    for i in sys.executable.split('\\')[:-1]:
        pip_path += i + '\\'
    pip_path += 'Scripts\\pip.exe'
    command = f'{sys.executable} {pip_path} install {moudle} -i {index}'
    return os_popen(command)
def uninstall(moudle=None):
    pip_path = ''

    for i in sys.executable.split('\\')[:-1]:
        pip_path += i + '\\'
    pip_path += 'Scripts\\pip.exe'
    command = f'{sys.executable} {pip_path} uninstall {moudle}'
    return os_popen(command)
def os_popen(strt):
    try:

        re = os.popen(strt).readlines()
        return re
    except BaseException as e:
        print(e)
if __name__ == '__main__':
    print(install('pip'))