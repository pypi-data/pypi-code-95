# -*- coding: utf-8 -*-  
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if "win" in sys.platform:
    install_requires=['pyserial',
        'Pillow',
        'freetype-py==2.1.0',
        'modbus-tk==1.1.2'
        ]
else:
    install_requires=['pyserial',
        'Pillow',
        'smbus',
        'spidev',
        'freetype-py==2.1.0',
        'evdev',
        'modbus-tk==1.1.2'
        ]


with open('README.md') as f:
    long_description = f.read()

setup(
    name='pinpong',
    packages=['pinpong','pinpong/base','pinpong/libs','pinpong/examples','pinpong/examples/xugu','pinpong/examples/nezha','pinpong/examples/RPi','pinpong/examples/handpy','pinpong/examples/microbit','pinpong/examples/GD32V','pinpong/examples/win','pinpong/extension/','pinpong/examples/PinPong Board/','pinpong/examples/PinPong Board/example/Many_board_control','pinpong/examples/PinPong Board/example/serial_example','pinpong/examples/PinPong Board/example/tcp_example'],
    install_requires=install_requires,

    include_package_data=True,
    entry_points={
      "console_scripts":["pinpong = pinpong.base.help:main"],
    },
    version='0.4.3',
    description="一个纯python实现的支持丰富外设的驱动库，支持win linux mac系统，支持arduino系列开发板，RPi、D1等linux开发板。附带丰富的使用例程",
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    python_requires = '>=3.5.*',
    author='Ouki Wang',
    author_email='ouki.wang@dfrobot.com',
    url='https://github.com/DFRobot/pinpong-docs',
    download_url='https://github.com/DFRobot/pinpong-docs',
    keywords=['Firmata', 'Arduino', 'Protocol', 'Python'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

