from setuptools import setup, find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='archijson', 
    version='0.1.2',
    packages=find_packages(),
    install_requires=['schema', 'python-socketio', 'requests', 'websocket-client'],
    description='ArchiJSON: A Light Weight Web Data Exchange Format for Architectrual Design',
    license='GNU General Public License v3.0',
    url='https://github.com/Inst-AAA/archijson',
    author='Yichen Mo',
    author_email='moyichen@seu.edu.cn',
    long_description=long_description,
    long_description_content_type = 'text/markdown',
    keywords=['architecture', 'engineering', 'design', 'json', 'exchange format'],

    project_urls={
        "ArchiWeb": "https://web.archialgo.com",
        "Documentation": "https://docs.web.archialgo.com",
        "Issues": "https://github.com/Inst-AAA/archijson/issues",
        "Repository": "https://github.com/Inst-AAA/archijson",
    },
        classifiers=[
        # https://pypi.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ],
)
