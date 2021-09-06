setup = '''
import setuptools, os

readme_path = 'README.md'

if os.path.exists(readme_path):
[TAB]with open(readme_path, 'r') as f:
[TAB][TAB]long_description = f.read()
else:
[TAB]long_description = '[PACKAGE_NAME]'

setuptools.setup(
[TAB]name='[PACKAGE_NAME]',
[TAB]version='[PACKAGE_VERSION]',
[TAB]author='[AUTHOR]',
[TAB]description='[SHORT_DESCRIPTION]',
[TAB]long_description=long_description,
[TAB]long_description_content_type='text/markdown',
[TAB]url='[GIT_URL]',
[TAB]packages=setuptools.find_packages(),
[TAB]install_requires=[[DEPENDENCIES]],
[TAB]classifiers=[
[TAB][TAB][PYTHON_CLASSIFIERS],
[TAB][TAB]'Operating System :: OS Independent',
[TAB]],
[TAB]python_requires='>=[MIN_PYTHON_VERSION]',
)
'''.strip()