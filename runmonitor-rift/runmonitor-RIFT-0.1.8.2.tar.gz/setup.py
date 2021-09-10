import setuptools

with open("README.md",'r') as fh:
    long_description = fh.read()

with open("requirements.txt",'r') as f:
    lines = f.readlines()
    for indx in range(len(lines)):
        lines[indx]=lines[indx].rstrip()
REQUIREMENTS={ 
"install" : lines 
#["python-daemon>=2.2.4","" 
} 

import glob
my_scripts = glob.glob("bin/*")

setuptools.setup(
    name="runmonitor-RIFT",
    version="0.1.8.2",
    author="Adhav Arulanandan, Grihith Manchanda, Richard O'Shaughnessy, Richard Udall, Joshua Brandt",
    author_email="rudall@caltech.edu",
    description="A package for monitoring RIFT PE runs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.ligo.org/richard.udall/runmonitor_rift",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", ],
    python_requires='>=3.7',
    install_requires=REQUIREMENTS["install"],
    scripts = my_scripts,
)


