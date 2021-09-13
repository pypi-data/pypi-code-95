import setuptools
from pathlib import Path
import subprocess

repo='modasci'

def GetVersion():
    version = Path(f'{repo}/VERSION').read_text().split('-')[0]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    commit = str(commit, "utf-8").strip()
    versionCommit = f'{version}-{commit}'
    Path(f'{repo}/VERSION').write_text(versionCommit)
    return version

setuptools.setup(
    name=repo,
    version=GetVersion(),
    description='Easy Logging Utility',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url=f'https://github.com/ArashLab/{repo}',
    author='Arash Bayat',
    author_email='a.bayat@garvan.org.au',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    include_package_data=True,
    install_requires=[],
    packages=setuptools.find_packages()
)