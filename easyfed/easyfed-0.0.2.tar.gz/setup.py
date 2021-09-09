import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="easyfed",
    version="0.0.2",
    author="kazgu",
    author_email="hasanjan@outlook.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kazgu/easyfed",
    packages=setuptools.find_packages(),
    package=['easyfed'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # scripts=['easyml/cortex/main.py'],
    entry_points={  # Optional
    'console_scripts': [
        'easyfed_server=easyfed:fedserver',
    ]
},
    install_requires=[
        'torch',
        'django',
        'requests',
    ]
# package_data={'': ['textcrawler/scrapy.cfg','textcrawler/textcrawler/ips.txt']}
# package_data={'': ['web_front/templates/*.*','web_front/static/assets/*/*','web_front/static/assets/*/*/*','web_front/static/assets/*/*/*/*','web_front/static/assets/*/*/*/*/*']}
    # package_data={'': ['meta_src/dataset.py', 'meta_src/main.py', 'meta_src/my_args.py','meta_src/train.py','meta_src/model.json','data/test/classification/train.tsv','data/test/classification/valid.tsv','data/test/classification/test.tsv','data/stop_words.txt','out/']},

#     data_files=[('~/.mlcortexdata/meta_src/', ['mlcortex/meta_src/dataset.txt', 'mlcortex/meta_src/main.txt','mlcortex/meta_src/my_args.txt','mlcortex/meta_src/train.txt','mlcortex/meta_src/model.json']),
#             ('~/.mlcortexdata/data/', ['mlcortex/data/test/classification/train.tsv','mlcortex/data/test/classification/valid.tsv','mlcortex/data/test/classification/test.tsv','mlcortex/data/stop_words.txt'])],
)