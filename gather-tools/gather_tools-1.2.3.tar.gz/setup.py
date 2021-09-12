from setuptools import setup, find_packages
setup(
    name="gather_tools",
    packages=find_packages(),
    version='1.2.3',
    description="Gather Tools",
    author="Merreel",
    long_description=open('README.md',encoding="utf-8").read(),
    author_email='1327444968@qq.com',
    # url="https://github.com/username/reponame",
    # download_url='https://github.com/username/reponame/archive/0.1.tar.gz',
    keywords=['command', 'line', 'tool'],
    classifiers=[],
    # entry_points={
    #     'console_scripts': [
    #     'command1 = gather_tools.cmdline:execute'
    # ]
    # },
    install_requires=[
        'selenium',
        'requests',
    ]
)