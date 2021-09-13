from setuptools import setup
with open('README.md','r',encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='downloader-python',
    version='1.0.9',
    url='https://github.com',
    long_description=long_description,
    author='mc_creater',
    author_email='guoxiuchen20170402@163.com',
    license='MIT',
    packages=['downloader-python','command'],
    classifiers=['Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3.8',
                 'Programming Language :: Python :: 3.9',],
    install_requires=['PyQt5','requests'],
    include_package_data=True

)