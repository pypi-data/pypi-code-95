from setuptools import setup, find_packages
from os import environ

setup_requires = [
]

install_requires = [
    'websockets',
    'click',
    'requests',
    'flask',
    'APScheduler',
    'dnspython'
]

dependency_links = [
]

setup(
    name='Ocean-Agent-Worker',
    version=environ["AGENT_VERSION"],
    description='Ocean-Agent for Worker nodes',
    author='kairos03',
    author_email='kairos9603@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    scripts=[],
    entry_points={
        'console_scripts': [
            'agent-worker = worker.main:cli'
            ],
        },
    )
