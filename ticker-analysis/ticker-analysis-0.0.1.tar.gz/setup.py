from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Open source library that calculates technical indicators for any ticker available on yahoo finance'

# Setting up
setup(
    name="ticker-analysis",
    version=VERSION,
    author="Andre Ceschia",
    author_email="andre.ceschia04@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['yfinance'],
    keywords=['python', 'finance', 'technical indicators', 'macd', 'bollinger bands', 'stocks', 'moving average', 'technical analysis'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)