from setuptools import setup, find_packages


VERSION = '0.0.1'
DESCRIPTION = 'Streaming video data via networks'
LONG_DESCRIPTION = 'A package that allows to build simple streams of video, audio and camera data.'

# Setting up
setup(
    name="ProSplit",
    version=VERSION,
    author="NeuralNine (Dyhanov Yaroslav)",
    author_email="<duhanov2003@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description="somt like that",
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],

)