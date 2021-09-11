from setuptools import setup
from os.path import join, dirname

setup(
    name='FoxHustle_QR',
    version='1.23',
    url="https://github.com/Fox-Hustle/QR-generator.git",
    description='QR-code Generator',
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    packages=['FoxHustle_QR'],
    license='MIT',
    author='DmitryKang',
    author_email='alexandrov.dp@mail.ru',
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Pillow==8.2.0', 
        'PyQRCode==1.2.1',
        'requests==2.23.0',
    ], 
    python_requires='>=3.6',
    )