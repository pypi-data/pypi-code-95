import setuptools

setuptools.setup(
    name="arxivbox",
    version="1.0.6",
    author="Ankan Kumar Bhunia",
    author_email="ankankumarbhunia@email.com",
    description="Deep learning paper finders",
    url="https://github.com/ankanbhunia/arxivbox",
    packages=setuptools.find_packages(),
    install_requires=['dash', 'dash_bootstrap_components' ,'feedparser', 'requests'               
                      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)