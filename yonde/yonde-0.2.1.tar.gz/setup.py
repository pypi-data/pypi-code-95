from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="yonde",
    version="0.2.1",
    author="yanhuishi",
    packages=['yonde', 'yonde/downloader', 'yonde/exceptions', 'yonde/extractors', 'yonde/images', 'yonde/main_class',
              'yonde/color', 'yonde/session'],
    author_email="contatoyonde@protonmail.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="Mangá downloader (para leitura offline) voltado para sites e scans brasileiros.",
    url="https://github.com/yonde-manga/yonde",
    download_url="https://github.com/yonde-manga/yonde/archive/refs/tags/v0.2.1.tar.gz",
    keywords=["manga", "downloader", "pdf"],
    entry_points={
        'console_scripts': [
            'yonde = yonde.__main__:main'
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'cloudscraper',
        'pillow',
        'lxml',
        'natsort',
        'cssselect',
        'colorama'
    ],
    python_requires=">=3.7",
)
