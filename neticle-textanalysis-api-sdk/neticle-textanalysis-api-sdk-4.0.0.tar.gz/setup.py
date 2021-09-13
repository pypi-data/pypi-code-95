import setuptools

def readme():
    with open('README.md', 'r') as f:
        return f.read()

setuptools.setup(
    name='neticle-textanalysis-api-sdk',
    version='4.0.0',
    license='MIT',
    description='Python SDK for Neticle Text Analysis API',
	long_description_content_type='text/markdown',
    long_description=readme(),
    url='https://neticle.com/textanalysisapi/en/',
    packages=setuptools.find_packages(),
    keywords=["nlp", "natural language processing", "text analysis", "sentiment analysis", "topic recognition"],
    install_requires=[
      'requests'
    ],
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = ">= 3.7",
    author='Neticle',
    author_email='dev@neticle.com'
)