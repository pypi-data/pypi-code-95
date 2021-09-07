from setuptools import setup, find_packages

VERSION = '1.0.7'
DESCRIPTION = 'module designed to make your data preprocessing experience easier'
with open("README.md") as description:
    LONG_DESCRIPTION = description.read()

# Setting up
setup(
    name="IslanderDataPreprocessing",
    version=VERSION,
    author="Islander Robotics (William McKeon",
    author_email="<IslanderRobotics@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["pandas","matplotlib","PyQt5","scikit-learn"],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)