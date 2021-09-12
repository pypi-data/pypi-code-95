from setuptools import setup
setup(
    name='pod_picker',
    version='0.0.1',
    author='gujitao',
    author_email='taojigu@163.com',
    url='https://github.com/taojigu',
    description=u'通过过对比壳工程podfile,生成正确的子工程podfile',
    packages=['pod_picker'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'demo_print=pod_picker:demo_print'
        ]
    }
)