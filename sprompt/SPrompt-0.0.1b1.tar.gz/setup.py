from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='SPrompt',
    version='0.0.1b1',
    description='ChokChaisak',
    long_description=readme(),
    url='https://github.com/ChokChaisak/ChokChaisak',
    author='ChokChaisak',
    author_email='ChokChaisak@gmail.com',
    license='ChokChaisak',
    install_requires=[
        'matplotlib',
        'numpy',
        'requests>=2.25.1',
        'keyboard>=0.13.5',
        'uiautomator2>=2.13.0',
        'webdriver-manager>=3.4.2',
        'robotframework-seleniumlibrary>=4.3.0',
    ],
    keywords='SPrompt',
    packages=['SPrompt'],
    package_dir={
    'SPrompt': 'src/SPrompt',
    },
    package_data={
    'SPrompt': ['*'],
    },
)