from setuptools import setup, find_packages
# import codecs
# import os

# here = os.path.abspath(os.path.dirname(__file__))

# with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#     long_description = "\n" + fh.read()

VERSION = '0.1.0'
DESCRIPTION = 'test'
LONG_DESCRIPTION = 'test'

# Setting up
# setup(
#     name="vidstream",
#     version=VERSION,
#     author="NeuralNine (Florian Dedov)",
#     author_email="<mail@neuralnine.com>",
#     description=DESCRIPTION,
#     long_description_content_type="text/markdown",
#     long_description=long_description,
#     packages=find_packages(),
#     install_requires=['opencv-python', 'pyautogui', 'pyaudio'],
#     keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
#     classifiers=[
#         "Development Status :: 1 - Planning",
#         "Intended Audience :: Developers",
#         "Programming Language :: Python :: 3",
#         "Operating System :: Unix",
#         "Operating System :: MacOS :: MacOS X",
#         "Operating System :: Microsoft :: Windows",
#     ]
# )


# from distutils.core import setup
setup(
    name='aaaaaatest',
    packages=[],
    version=VERSION,
    description=DESCRIPTION,
    author='Kouros Basisi',
    author_email='kouros.basiri@d.con',
    url='https://github.com/kourosa/data_package.git',
    keywords=[ 'test' ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development',
    ],
)
