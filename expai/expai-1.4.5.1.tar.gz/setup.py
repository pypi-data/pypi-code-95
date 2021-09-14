from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='expai',
    version='1.4.5.1',
    description='User-friendly library to interact with EXPAI',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='EXPAI',
    author_email='info@expai.io',
    keywords=['EXPAI', 'ExplainableAI', 'Explainable Artificial Intelligence'],
    url='https://expai.io',
    download_url='https://pypi.org/project/expai/'
)

install_requires = ['requests', 'ipython', 'pandas', 'numpy', 'plotly']

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)