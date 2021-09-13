from setuptools import setup, find_packages

setup(name='archijson', 
    version='0.1.0',
    packages=find_packages(),
    install_requires=['schema', 'python-socketio', 'requests', 'websocket-client'],
    description='ArchiJSON: A Light Weight Web Data Exchange Format for Architectrual Design',
    license='GNU General Public License v3.0',
    url='https://github.com/Inst-AAA/archijson',
    author='Yichen Mo',
    author_email='moyichen@seu.edu.cn',
    
)
