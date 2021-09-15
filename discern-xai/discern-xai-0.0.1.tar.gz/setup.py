import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
     name='discern-xai',
     version='0.0.1',
     author="Anjana Wijekoon",
     author_email="a.wijekoon1@rgu.ac.uk",
     description="DisCERN: Discovering Counterfactual Explanations using Relevance Features from Neighbourhoods",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/anjanaw/discern",
     packages=setuptools.find_packages(exclude=("test",)),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
     ],
 )
