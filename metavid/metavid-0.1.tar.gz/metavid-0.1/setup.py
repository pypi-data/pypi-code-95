from setuptools import setup, find_packages

CLASSIFIERS = """
Development Status :: 1 - Planning
Intended Audience :: Other Audience
Intended Audience :: Developers
License :: OSI Approved :: BSD License

Programming Language :: Python :: 3.6
Topic :: Software Development
Topic :: Education :: Computer Aided Instruction (CAI)
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS
"""

with open("README.md", "r", encoding="utf-8") as fh:
   long_description = fh.read()


setup(
    name='metavid',
    version=' 0.1',
    author='Dr. Rico Picone',
    author_email='rpicone@stmartin.edu',
    url='https://github.com/dialectic/metavid',
    description='Tool for adding metastimuli to videos',
    long_description=long_description,
	long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[f for f in CLASSIFIERS.split('\n') if f],
    install_requires=['ffmpeg-python','numpy','scipy','matplotlib'],
)