from setuptools import setup

SET_UP_ATTRS = dict(
    name='regia',
    version='0.1.0',
    author='eat-more-apple',
    author_email='wannieqing@sailingmarvel.onaliyun.com',
    packages=['regia', 'regia.plugins'],
    url="http://106.75.251.250:8081/nieqing/regia",
    install_requires=(
        'django==3.2.7',
        'flask==2.0.1',
        'pymongo==3.12.0',
        'simplejson==3.17.5',
        'nacos-sdk-python==0.1.6',
        'mysqlclient==2.0.3',
    )
)

# 项目打包发布
setup(**SET_UP_ATTRS)
