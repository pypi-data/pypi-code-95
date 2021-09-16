from setuptools import setup

setup(
    name='auto-mock-server',
    version="1.0.5",
    license='MIT',
    description='In order to solve the interface dependence of interface test',

    long_description_content_type='text/markdown',
    url='https://github.com/zhujiahuan/mock-server',
    author='zhujiahuan',
    author_email='zhujiahuan@yfcloud.com',
    py_modules = ["mock"],
    install_requires=[
        "requests==2.25.1",
        "paramiko==2.7.2",
        "Flask==1.1.2",
        "pytest>=3.6"

    ]

)
