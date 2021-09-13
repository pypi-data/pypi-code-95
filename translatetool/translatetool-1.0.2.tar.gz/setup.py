from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(name='translatetool',
version='1.0.2',
description='A Papago Translate module.',
author='Jaewoo Lee',
author_email='jaewoolee82@kakao.com',
url='https://github.com/jaewoolee82/translatetool',
license='MIT',
py_modules=['translatetool'],
python_requires='>=3',
install_requires=['aiohttp'],
packages=['translatetool'],
long_description=long_description,
long_description_content_type='text/markdown'
)