from distutils.core import setup
setup(
    name="fluxhelper",
    packages=["fluxhelper"],
    version="0.1",
    license="MIT",
    description="Helper library made for my projects",
    author="Philippe Mathew",
    author_email="philmattdev@gmail.com",
    url="https://github.com/bossauh/fluxhelper/releases/tag/v_01",
    download_url="https://github.com/bossauh/fluxhelper/archive/refs/tags/v_01.tar.gz",
    keywords=["helper"],
    install_requires=[
        "pycaw",
        "termcolor"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
