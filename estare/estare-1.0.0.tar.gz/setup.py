import setuptools
#TODO Fix the Cython lib
from distutils import core
from distutils.extension import Extension
#from Cython.Distutils import build_ext



with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="estare", 
    version="1.0.0",
    author="Soheil Soltani",    
    description="Package for image alignment and stacking which can be used from the linux command-line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/soheil-soltani/estare",
    packages=setuptools.find_packages(exclude="tests",),    
    classifiers=[
        "Programming Language :: Python :: 3",
	"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    install_requires=[
        'numpy>=1.19.2',
        'matplotlib>=3.3.2',
        'scikit-image>=0.17.2',        
    ],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts' : ['estare=estare.__main__:main']
    }
)

#core.setup(
#    cmdclass = {'build_ext' : build_ext},
#    ext_modules = [Extension("calculate", ["estare/src/arc.pyx"])]
#    )

